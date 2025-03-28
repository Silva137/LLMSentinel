from datetime import datetime
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
COOKIES = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyOTQyNDgzNTQyLCJpYXQiOjE3NDI0ODM1NDIsImp0aSI6Ijg1ZDJiOWViYzAzZjQ4OTFhOTk2YTY3NDgwMjgwMzBiIiwidXNlcl9pZCI6MX0.oMkX5jaihoSHvY-I7wLrgOvfZCmtKyzjRoAxG7p8IiQ"
}

models = [
    "OpenAI: GPT-3.5 Turbo",
    "OpenAI: GPT-4o-mini",
    "Google: Gemini Flash 2.0",
    "Mistral: Mistral Small 3.1 24B",
    "Meta: Llama 3.3 70B Instruct",
    "Google: Gemma 3 27B",
    "Qwen2.5 7B Instruct"
]

dataset_names = [
    "Applications Security",
    "Cloud Security",
    "Cryptography",
    "Digital Forensics",
    "Iam",
    "Network Security",
    "Operating Systems Security",
    #"tiago.csv",
    #"Secqa V1",
    #"Secqa V2",
    #"Cybermetric 80",
    #"Seceval",
    #"Secmmlu",
    #"Cyquiz",
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

            # Extract class-wise metrics
            class_metrics = data.get("class_metrics", {})
            class_precision = {k: v.get("precision", None) for k, v in class_metrics.items()}
            class_recall = {k: v.get("recall", None) for k, v in class_metrics.items()}
            class_f1 = {k: v.get("f1-score", None) for k, v in class_metrics.items()}

            # Extract answer distribution
            answer_distribution = data.get("answer_distribution", {})
            started_at = data.get("started_at", "")
            completed_at = data.get("completed_at", "")

            start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
            test_duration = (end - start).total_seconds()

            results.append({
                "dataset_name": dataset_name,
                "model": model,
                "accuracy": accuracy,
                "f1_score": f1_score,
                "precision": precision,
                "recall": recall,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "class_precision": class_precision,
                "class_recall": class_recall,
                "class_f1": class_f1,
                "answer_distribution": answer_distribution,
                "duration_seconds": test_duration
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
    """Generates bar plots for model accuracy, precision, recall"""

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



def generate_performance_heatmap(df):
    model_name_mapping = {
        "OpenAI: GPT-3.5 Turbo": "GPT-3.5",
        "OpenAI: GPT-4o-mini": "GPT-4o-mini",
        "Google: Gemini Flash 2.0": "Gemini Flash 2.0",
        "Mistral: Mistral Small 3.1 24B": "Mistral 3.1 24B",
        "Meta: Llama 3.3 70B Instruct": "Llama 3.3 70B",
        "Google: Gemma 3 27B": "Gemma 3 27B",
        "Qwen2.5 7B Instruct": "Qwen2.5 7B"
    }

    # Replace model names in the DataFrame
    df["model"] = df["model"].replace(model_name_mapping)

    df_pivot = df.pivot(index="dataset_name", columns="model", values="correct_answers")

    # Create the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(df_pivot, annot=True, cmap="coolwarm", fmt="d", linewidths=0.5, cbar_kws={'label': 'Correct Answers'})

    # Customize plot appearance
    plt.xlabel("LLM Model", fontsize=12)
    plt.ylabel("Dataset", fontsize=12)
    plt.title("Heatmap of Correct Answers per Model Across Datasets", fontsize=16)

    plt.savefig("heatmap_correct_answers.png")
    plt.close()
    print("✅ Heatmap saved")

def generate_dataset_bar_chart(df):
    """Generates a grouped bar chart showing model performance across datasets with values on top of bars."""

    # Define a dictionary to map full model names to simpler ones
    model_name_mapping = {
        "OpenAI: GPT-3.5 Turbo": "GPT-3.5",
        "OpenAI: GPT-4o-mini": "GPT-4o-mini",
        "Google: Gemini Flash 2.0": "Gemini Flash",
        "Mistral: Mistral Small 3.1 24B": "Mistral 3.1",
        "Meta: Llama 3.3 70B Instruct": "Llama 3.3",
        "Google: Gemma 3 27B": "Gemma 3",
        "Qwen2.5 7B Instruct": "Qwen2.5"
    }

    # Replace model names in the DataFrame
    df["model"] = df["model"].replace(model_name_mapping)

    # Plot settings
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="model", y="accuracy", hue="dataset_name", data=df, palette="Set1")

    # Add values on top of bars
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # Avoid displaying numbers for zero values
            ax.annotate(f"{height:.1f}%",
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, color="black")

    # Formatting
    plt.xlabel("LLM Model", fontsize=12)
    plt.ylabel("Accuracy (%)", fontsize=12)
    plt.xticks(rotation=30, ha="right", fontsize=10)
    plt.yticks(range(30, 110, 10))
    plt.title("LLM Performance Across Cybersecurity Datasets", fontsize=14)
    plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Save and show the plot
    output_path = os.path.join("./", "dataset_performance_chart.png")
    plt.savefig(output_path, bbox_inches="tight")
    print(f"✅ Bar chart saved as {output_path}")


def generate_answer_distribution_chart(df):
    """Generates a stacked bar chart showing the distribution of model responses including invalid answers ('X')."""

    model_name_mapping = {
        "OpenAI: GPT-3.5 Turbo": "GPT-3.5",
        "OpenAI: GPT-4o-mini": "GPT-4o-mini",
        "Google: Gemini Flash 2.0": "Gemini Flash 2.0",
        "Mistral: Mistral Small 3.1 24B": "Mistral 3.1 24B",
        "Meta: Llama 3.3 70B Instruct": "Llama 3.3 70B",
        "Google: Gemma 3 27B": "Gemma 3 27B",
        "Qwen2.5 7B Instruct": "Qwen2.5 7B"
    }

    # Convert the answer distribution column from JSON strings to dictionaries
    answer_data = []
    for _, row in df.iterrows():
        answer_distribution = json.loads(row["answer_distribution"])
        answer_distribution["Model"] = model_name_mapping.get(row["model"], row["model"])  # Map model names
        answer_data.append(answer_distribution)

    answer_df = pd.DataFrame(answer_data)

    # Melt the data to long format for seaborn plotting
    answer_df = answer_df.melt(id_vars=["Model"], var_name="Answer", value_name="Count")

    # Plot settings
    plt.figure(figsize=(12, 6))
    sns.barplot(x="Model", y="Count", hue="Answer", data=answer_df, palette="coolwarm")

    # Formatting
    plt.xlabel("")
    plt.ylabel("Answer Count", fontsize=12)
    plt.xticks(rotation=30, ha="right", fontsize=10)
    plt.title("LLM Answer Distribution Across Datasets", fontsize=14)
    plt.legend(title="Answer Option", bbox_to_anchor=(1.05, 1), loc="upper left")

    # Save and show the plot
    output_path = os.path.join("./", "answer_distribution_chart.png")
    plt.savefig(output_path, bbox_inches="tight")
    print(f"✅ Answer distribution chart saved as {output_path}")

def generate_execution_time_chart(df):
    """Gera gráfico de barras com o tempo de execução dos testes por modelo e dataset."""
    model_name_mapping = {
        "OpenAI: GPT-3.5 Turbo": "GPT-3.5",
        "OpenAI: GPT-4o-mini": "GPT-4o-mini",
        "Google: Gemini Flash 2.0": "Gemini Flash",
        "Mistral: Mistral Small 3.1 24B": "Mistral 3.1",
        "Meta: Llama 3.3 70B Instruct": "Llama 3.3",
        "Google: Gemma 3 27B": "Gemma 3",
        "Qwen2.5 7B Instruct": "Qwen2.5"
    }

    df["model"] = df["model"].replace(model_name_mapping)

    plt.figure(figsize=(12, 6))
    sns.barplot(x="model", y="duration_seconds", hue="dataset_name", data=df, palette="Set3")

    plt.xlabel("Modelo", fontsize=12)
    plt.ylabel("Duração (segundos)", fontsize=12)
    plt.title("LLM Execution Time Across Cybersecurity Datasets", fontsize=14)
    plt.xticks(rotation=30, ha="right")
    plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()
    output_path = os.path.join("./", "execution_time_chart.png")
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Execution time chart saved as {output_path}")



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
    print_model_comparison_table(df)
    generate_dataset_bar_chart(df)
    generate_answer_distribution_chart(df)
    generate_execution_time_chart(df)

    print("Evaluation process completed successfully!")


if __name__ == "__main__":
    main()
