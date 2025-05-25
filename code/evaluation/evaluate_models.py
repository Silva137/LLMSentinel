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
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyOTQ2MTIwNDI0LCJpYXQiOjE3NDYxMjA0MjQsImp0aSI6Ijk1ZDcwZDViMzdjZTRhZmQ5ODkyYzliNjlkYzcwY2NiIiwidXNlcl9pZCI6MX0.AbbXfqf1TD0eEOwxpkGXTJXO6QSiWVirNFfc5IqbFR4"
}

models1 = [
    "OpenAI: GPT-3.5 Turbo",
    "OpenAI: GPT-4o-mini",
    "Google: Gemini Flash 2.0",
    "Mistral: Mistral Small 3.1 24B",
    "Meta: Llama 3.3 70B Instruct",
    "Google: Gemma 3 27B",
    "Qwen2.5 7B Instruct"
]

models2 = [
    "OpenAI: GPT-4o",
    "OpenAI: GPT-4o-mini",
    "Anthropic: Claude 3.7 Sonnet",
    "Anthropic: Claude 3.5 Haiku",
    "Google: Gemini 2.5 Pro Preview",
    "Google: Gemini 2.0 Flash",
    "xAI: Grok 3 Beta",
    "xAI: Grok 3 Mini Beta",
    "Mistral Large 2411",
    "Mistral: Mistral Small 3.1 24B",
]

dataset_names = [
    "Applications Security",
    "Cloud Security",
    "Cryptography",
    "Digital Forensics",
    "Iam",
    "Network Security",
    "Operating Systems Security",
    #"Malware",
    #"Ctf",
    #"Honeypots",
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
        for model in models2:
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
                    print(f"Error for {model} on Dataset {dataset_name}: {e}")
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

    model_name_map = {
        "OpenAI: GPT-4o": "GPT-4o",
        "OpenAI: GPT-4o-mini": "GPT-4o Mini",
        "Anthropic: Claude 3.7 Sonnet": "Claude 3.7 Sonnet",
        "Anthropic: Claude 3.5 Haiku": "Claude 3.5 Haiku",
        "Google: Gemini 2.5 Pro Preview": "Gemini 2.5 Pro",
        "Google: Gemini 2.0 Flash": "Gemini 2.0 Flash",
        "xAI: Grok 3 Beta": "Grok 3",
        "xAI: Grok 3 Mini Beta": "Grok 3 Mini",
        "Mistral Large 2411": "Mistral Large",
        "Mistral: Mistral Small 3.1 24B": "Mistral Small"
    }

    df["model"] = df["model"].apply(lambda name: model_name_map.get(name, name))

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


def generate_average_accuracy_chart(df):
    """
    Generates a bar chart showing the average accuracy per model across all evaluated datasets.
    """
    if df.empty:
        print("DataFrame is empty. Skipping average accuracy chart generation.")
        return

    # Calculate the average accuracy for each model
    # Group by 'model' and calculate the mean of 'accuracy'
    # .reset_index() converts the grouped result back into a DataFrame
    avg_accuracy_df = df.groupby('model')['accuracy'].mean().reset_index()

    # Sort models by average accuracy for better visualization (optional)
    avg_accuracy_df = avg_accuracy_df.sort_values('accuracy', ascending=False)

    # Plotting
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6)) # Adjust figure size as needed

    # Create the bar plot
    ax = sns.barplot(
        x='model',
        y='accuracy',
        data=avg_accuracy_df,
        palette='viridis' # You can choose a different color palette
    )

    # Add the average accuracy value on top of each bar
    for p in ax.patches:
        height = p.get_height()
        if pd.notna(height): # Check if height is NaN before annotating
            ax.annotate(f'{height:.1f}', # Format to one decimal place
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=10, color='black',
                        xytext=(0, 3), # 3 points vertical offset
                        textcoords='offset points')

    # Formatting
    plt.xlabel("Model", fontsize=12)
    plt.ylabel("Average Accuracy (%) Across Datasets", fontsize=12)
    plt.title("Average Model Accuracy Across All Evaluated Datasets", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=10) # Rotate labels if they overlap
    plt.ylim(0, 105) # Set y-axis limit slightly above 100%
    plt.tight_layout() # Adjust layout to prevent labels overlapping

    # Save the plot
    output_path = os.path.join("./", "average_accuracy_per_model.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Average accuracy per model chart saved as {output_path}")


def generate_dataset_bar_chart(df):
    """Generates a grouped bar chart showing model performance across datasets with values on top of bars."""

    # Plot settings
    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="model", y="accuracy", hue="dataset_name", data=df, palette="Set1")


    # Add values on top of bars
    #for p in ax.patches:
    #    height = p.get_height()
    #    if height > 0:  # Avoid displaying numbers for zero values
    #        ax.annotate(f"{height:.0f}",
    #                    (p.get_x() + p.get_width() / 2., height + 0.5),
    #                    ha='center', va='bottom', fontsize=11, color="black")


    # Formatting
    plt.ylabel("Accuracy (%)", fontsize=15)
    plt.xlabel("", fontsize=14)
    plt.xticks(rotation=15, ha="center", fontsize=15)

    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
        frameon=False,
        fontsize=13
    )
    plt.tight_layout()

    # Save and show the plot
    output_path = os.path.join("./", "dataset_performance_chart.png")
    plt.savefig(output_path, bbox_inches="tight")
    print(f"✅ Bar chart saved as {output_path}")



def generate_execution_time_chart(df):
    """Gera gráfico de barras com o tempo de execução dos testes por modelo e dataset."""

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="model", y="duration_seconds", hue="dataset_name", data=df, palette="Set2")

    # Adiciona os valores de duração acima das barras
    #for container in ax.containers:
    #    ax.bar_label(container, fmt="%.0f", label_type="edge", fontsize=11, padding=3)

    plt.ylabel("Duration (seconds)", fontsize=15)
    plt.xlabel("", fontsize=15)
    plt.xticks(rotation=15, ha="center", fontsize=15)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
        frameon=False,
        fontsize=13
    )

    plt.tight_layout()
    output_path = os.path.join("./", "execution_time_chart.png")
    plt.savefig(output_path)
    plt.close()
    print(f"✅ Execution time chart saved as {output_path}")


def print_model_comparison_table(df):
    """Prints a table summarizing the model performance across datasets, including answer distribution."""
    table = df[["dataset_name", "model", "accuracy", "precision", "recall", "f1_score", "answer_distribution"]].copy()

    # Convert the answer_distribution JSON strings back to dictionaries and format them for display
    table["answer_distribution"] = table["answer_distribution"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else x)
    table["answer_distribution"] = table["answer_distribution"].apply(
        lambda x: ", ".join([f"{k}: {v}" for k, v in x.items()]))

    # Print the table using tabulate
    print(tabulate.tabulate(table, headers="keys", tablefmt="pretty", showindex=True))


def main():
    print("Starting LLM Model Evaluation...")

    results = evaluate_models()

    df = save_results(results)

    generate_bar_charts(df)
    generate_average_accuracy_chart(df)
    print_model_comparison_table(df)
    generate_dataset_bar_chart(df)
    generate_execution_time_chart(df)

    print("Evaluation process completed successfully!")


if __name__ == "__main__":
    main()
