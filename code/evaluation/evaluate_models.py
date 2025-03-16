import matplotlib
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import tabulate

matplotlib.use('Agg')

API_URL = "http://localhost:8001/api/tests/"
LOGIN_URL = "http://localhost:8001/api/auth/login/"
COOKIES = {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcyMTM1Njg1LCJpYXQiOjE3NDIxMzU2ODUsImp0aSI6ImRlNjliODA0MDUxYTRkMDI4ZDdkZWYxNTUzY2U5NTFhIiwidXNlcl9pZCI6MX0.mhswhlgGfQM48FALelaJ4ET9kL9HvRp0VdUnFQ2BPAI"}


models = [
    "OpenAI: GPT-4o-mini",
    "Google: Gemini Flash 2.0",
    "Mistral: Mixtral 8x7B (base)",
    "Meta: Llama 3.3 70B Instruct",
]

dataset_names = [
    #"Applications Security",
    #"Cloud Security",
    #"Cryptography",
    #"Digital Forensics",
    #"Iam",
    #"Network Security",
    #"Operating Systems Security",
    #"tiago.csv",
    #"Secqa V1",
    "Secqa V2",
    #"Cybermetric 80",
    #"Seceval",
    #"Secmmlu",
    #"Cyquiz"
]

def get_existing_test(dataset_name, model):
    """Check if a test already exists for a given dataset and model."""

    response = requests.get(API_URL, params={"dataset_name": dataset_name, "llm_model_name": model}, cookies=COOKIES)

    if response.status_code == 200:
        tests = response.json()  # Gets the list of tests

        if tests:  # If there are any results, return the first test
            print(f"Found existing test for {model} on Dataset {dataset_name}")
            return tests[0]  # Take only the first test

    return None  # No existing test found


def evaluate_models():
    """Runs the evaluation process for multiple models and datasets, retrieving existing tests when available."""
    results = []

    for dataset_name in dataset_names:
        for model in models:
            existing_test = get_existing_test(dataset_name, model)

            if existing_test:
                data = existing_test
            else:
                body = {"dataset_name": dataset_name, "llm_model_name": model}
                print(f"Evaluating {model} on Dataset {dataset_name}...")

                try:
                    response = requests.post(API_URL, json=body, cookies=COOKIES)

                    if response.status_code == 201:
                        data = response.json()
                        print(f"Success: {model} on Dataset {dataset_name}")
                    else:
                        print(f"Failed for {model} on Dataset {dataset_name} - {response.status_code}")
                        continue

                except Exception as e:
                    print(f"⚠️ Error for {model} on Dataset {dataset_name}: {e}")
                    continue

                time.sleep(1)

            # Extract evaluation metrics
            accuracy = data.get("accuracy_percentage", None)
            f1_score = data.get("f1_avg", None)
            precision = data.get("precision_avg", None)
            recall = data.get("recall_avg", None)
            correct_answers = data.get("correct_answers", None)
            total_questions = sum(data.get("answer_distribution", {}).values())

            # New Confidence Metrics
            avg_confidence = data.get("avg_confidence", None)
            confidence_weighted_accuracy = data.get("confidence_weighted_accuracy", None)

            # Extract class-wise metrics
            class_metrics = data.get("class_metrics", {})
            class_precision = {k: v.get("precision", None) for k, v in class_metrics.items()}
            class_recall = {k: v.get("recall", None) for k, v in class_metrics.items()}
            class_f1 = {k: v.get("f1-score", None) for k, v in class_metrics.items()}

            # Extract answer distribution
            answer_distribution = data.get("answer_distribution", {})

            results.append({
                "dataset_name": dataset_name,
                "model": model,
                "accuracy": accuracy,
                "f1_score": f1_score,
                "precision": precision,
                "recall": recall,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "avg_confidence": avg_confidence,
                "confidence_weighted_accuracy": confidence_weighted_accuracy,
                "class_precision": class_precision,
                "class_recall": class_recall,
                "class_f1": class_f1,
                "answer_distribution": answer_distribution
            })

    return results


def save_results(results):
    """Saves evaluation results to CSV."""
    df = pd.DataFrame(results)

    df["class_precision"] = df["class_precision"].apply(json.dumps)
    df["class_recall"] = df["class_recall"].apply(json.dumps)
    df["class_f1"] = df["class_f1"].apply(json.dumps)
    df["answer_distribution"] = df["answer_distribution"].apply(json.dumps)

    df.to_csv("evaluation_results.csv", index=False)
    print("✅ Results saved to evaluation_results.csv")
    return df


def generate_bar_charts(df):
    """Generates bar plots for model accuracy, precision, recall, and answer distribution."""

    output_dir = "./"
    sns.set(style="whitegrid")

    # **Accuracy Comparison**
    plt.figure(figsize=(12, 6))
    sns.barplot(x="dataset_name", y="accuracy", hue="model", data=df, palette="Set2")
    plt.xlabel("Dataset Name", fontsize=12)
    plt.ylabel("Accuracy (%)", fontsize=12)
    plt.title("Model Accuracy Across Datasets", fontsize=14)
    plt.legend(title="LLM Model")
    plt.savefig(os.path.join(output_dir, "accuracy_comparison.png"))
    plt.close()

    # **Precision, Recall, and F1-score**
    metrics = ["precision", "recall", "f1_score"]
    for metric in metrics:
        plt.figure(figsize=(12, 6))
        sns.barplot(x="dataset_name", y=metric, hue="model", data=df, palette="Set1")
        plt.xlabel("Dataset Name", fontsize=12)
        plt.ylabel(f"{metric.capitalize()} Score", fontsize=12)
        plt.title(f"{metric.capitalize()} Across Models and Datasets", fontsize=14)
        plt.legend(title="LLM Model")
        plt.savefig(os.path.join(output_dir, f"{metric}_comparison.png"))
        plt.close()

    # **Answer Distribution (Stacked Bar Chart)**
    answer_options = ["A", "B", "C", "D"]

    distribution_df = pd.DataFrame([
        {
            "dataset_name": row["dataset_name"],
            "model": row["model"],
            **json.loads(row["answer_distribution"])
        }
        for _, row in df.iterrows()
    ])

    distribution_df_melted = distribution_df.melt(id_vars=["dataset_name", "model"], value_vars=answer_options,
                                                  var_name="Answer Option", value_name="Count")

    plt.figure(figsize=(12, 6))
    sns.barplot(x="dataset_name", y="Count", hue="Answer Option", data=distribution_df_melted, palette="coolwarm")
    plt.xlabel("Dataset Name", fontsize=12)
    plt.ylabel("Answer Distribution Count", fontsize=12)
    plt.title("Answer Distribution Across Datasets", fontsize=14)
    plt.legend(title="Answer Option")
    plt.savefig(os.path.join(output_dir, "answer_distribution.png"))
    plt.close()

    print("✅ Bar plots saved successfully in the current folder.")


def generate_performance_heatmap(df):
    df_pivot = df.pivot(index="dataset_name", columns="model", values="correct_answers")

    # Create the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(df_pivot, annot=True, cmap="coolwarm", fmt="d", linewidths=0.5, cbar_kws={'label': 'Correct Answers'})

    # Customize plot appearance
    plt.xlabel("LLM Model", fontsize=12)
    plt.ylabel("Dataset", fontsize=12)
    plt.title("Heatmap of Correct Answers per Model Across Datasets", fontsize=14)

    plt.savefig("heatmap_correct_answers.png")
    plt.close()
    print("✅ Heatmap saved")


def generate_confidence_accuracy_bar_chart(df):
    """Generates a bar chart for confidence-weighted accuracy."""
    plt.figure(figsize=(12, 6))
    sns.barplot(x="dataset_name", y="confidence_weighted_accuracy", hue="model", data=df, palette="Set3")
    plt.xlabel("Dataset Name", fontsize=12)
    plt.ylabel("Confidence-Weighted Accuracy (%)", fontsize=12)
    plt.title("Confidence-Weighted Accuracy Across Models", fontsize=14)
    plt.legend(title="LLM Model")
    plt.savefig("confidence_weighted_accuracy.png")
    plt.close()
    print("Confidence-Weighted Accuracy Bar Chart saved")


def print_model_comparison_table(df):
    """Prints a table summarizing the model performance across datasets."""
    table = df[["dataset_name", "model", "accuracy", "precision", "recall", "f1_score"]]
    print(tabulate.tabulate(table, headers="keys", tablefmt="pretty"))


def main():
    print("Starting LLM Model Evaluation...")

    results = evaluate_models()

    df = save_results(results)

    generate_bar_charts(df)
    generate_performance_heatmap(df)
    generate_confidence_accuracy_bar_chart(df)
    print_model_comparison_table(df)

    print("Evaluation process completed successfully!")


if __name__ == "__main__":
    main()
