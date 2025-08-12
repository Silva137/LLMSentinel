import matplotlib
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
from tabulate import tabulate


matplotlib.use('Agg')

COOKIES = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU1OTU5NDA1LCJpYXQiOjE3NTMzNjc0MDUsImp0aSI6IjEyZjI5N2U2NTg5ZTRjYmRhMTdhNTgwOWFjYjhhZmQzIiwidXNlcl9pZCI6MX0.zEZEQYu3yabZYg-5Cjj0cWa9Re5XAaC7YJJgiiSYzUY"
}

models2 = [
    "OpenAI: GPT-4o",
    "OpenAI: GPT-4o-mini",
    "Anthropic: Claude 3.7 Sonnet",
    "Anthropic: Claude 3.5 Haiku",
    "Google: Gemini 2.5 Pro",
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
    "Malware",
    "Ctf",
    "Honeypots",
    "Secqa V1",
    "Secqa V2",
    #"Cybermetric 80",
    #"Seceval",`
    "Secmmlu",
    "Cyquiz",
]

model_name_map = {
    "OpenAI: GPT-4o": "GPT-4o",
    "OpenAI: GPT-4o-mini": "GPT-4o Mini",
    "Anthropic: Claude 3.7 Sonnet": "Claude 3.7 Sonnet",
    "Anthropic: Claude 3.5 Haiku": "Claude 3.5 Haiku",
    "Google: Gemini 2.5 Pro": "Gemini 2.5 Pro",
    "Google: Gemini 2.0 Flash": "Gemini 2.0 Flash",
    "xAI: Grok 3 Beta": "Grok 3",
    "xAI: Grok 3 Mini Beta": "Grok 3 Mini",
    "Mistral Large 2411": "Mistral Large 2411",
    "Mistral: Mistral Small 3.1 24B": "Mistral Small 3.1"
}


def get_existing_tests(dataset_name, model):
    """Check if a test already exists for a given dataset and model."""

    response = requests.get("http://localhost:8001/api/tests/",
                            params={"dataset_name": dataset_name, "llm_model_name": model}, cookies=COOKIES)

    if response.status_code == 200:
        tests = response.json()  # Gets the list of tests

        if tests:
            print(f"Found {len(tests)} test(s) for {model} on Dataset {dataset_name}")
            return tests

    return []  # No existing test found


def get_or_run_tests(dataset_name, model, required_tests=3):
    """
    Ensure that there are at least `required_tests` for the given dataset and model.
    If not, execute additional tests via the POST API until the total count is met.
    Returns a list with the final (at least required) tests.
    """
    tests = get_existing_tests(dataset_name, model)

    while len(tests) < required_tests:
        # Run a new test.
        body = {"dataset_name": dataset_name, "llm_model_name": model}
        print(f"Evaluating {model} on Dataset {dataset_name}... (new test)")
        try:
            response = requests.post("http://localhost:8001/api/tests/", json=body, cookies=COOKIES)
            if response.status_code == 201:
                new_test = response.json()
                tests.append(new_test)
                print(f"Success: {model} on Dataset {dataset_name} (total tests now: {len(tests)})")
            else:
                print(f"Failed to run test for {model} on Dataset {dataset_name} - HTTP {response.status_code}")
                break
        except Exception as e:
            print(f"Error running test for {model} on Dataset {dataset_name}: {e}")
            break
        time.sleep(1)

    return tests[-required_tests:]


def evaluate_models():
    """Runs the evaluation process for multiple models and datasets, retrieving existing tests when available."""
    results = []

    for dataset_name in dataset_names:
        for model in models2:
            tests = get_or_run_tests(dataset_name, model, required_tests=3)
            #print answer distribution of each test
            for test in tests:
                print(f"Test ID: {test['id']}, Answer Distribution: {test.get('answer_distribution', 'N/A')}")
            if not tests:
                print(f"Skipping {model} on Dataset {dataset_name} because no tests could be obtained.")
                continue

            # Step 2: Get average/median performance from external API
            try:
                response = requests.get(
                    "http://localhost:8001/api/results/model-average-performance-on-dataset/",
                    params={
                        "model_name": model,
                        "dataset_name": dataset_name
                    }, cookies=COOKIES
                )
                response.raise_for_status()
                avg_data = response.json()

                results.append({
                    "model_name": avg_data.get("modelName"),
                    "dataset_name": avg_data.get("datasetName"),
                    "average_accuracy": avg_data.get("averageAccuracyPercentage"),
                    "average_duration_seconds": avg_data.get("averageDurationSeconds"),
                    "confidence_interval_low": avg_data.get("confidenceIntervalLow"),
                    "confidence_interval_high": avg_data.get("confidenceIntervalHigh"),
                    "number_of_executions": avg_data.get("numberOfExecutions")
                })
            except Exception as e:
                print(f"Error fetching average data for {model} on {dataset_name}: {e}")

    return results


def save_results(results):
    """Saves evaluation results to CSV."""
    df = pd.DataFrame(results)

    df["model"] = df["model_name"].apply(lambda name: model_name_map.get(name, name))
    df.rename(columns={
        "average_accuracy": "accuracy",
        "average_duration_seconds": "duration_seconds"
    }, inplace=True)

    df.to_csv("evaluation_results.csv", index=False)
    print("Results saved to evaluation_results.csv")
    return df


def generate_confidence_interval_plot(df):
    """
    Gera gráfico com pontos de accuracy e intervalos de confiança (95%) agrupando por modelo,
    com offset por dataset, ordenado por média de accuracy, com separadores e espaçamento ajustado.
    """
    if df.empty:
        print("DataFrame vazio. Gráfico de IC não gerado.")
        return

    df["model"] = df["model"].replace(model_name_map)
    df = df.dropna(subset=["accuracy", "confidence_interval_low", "confidence_interval_high"]).copy()
    df["ci_minus"] = df["accuracy"] - df["confidence_interval_low"]
    df["ci_plus"] = df["confidence_interval_high"] - df["accuracy"]

    # Ordenar modelos por média de accuracy
    model_order = df.groupby("model")["accuracy"].mean().sort_values(ascending=False).index.tolist()
    model_to_x = {model: idx for idx, model in enumerate(model_order)}

    # Dataset offsets e cores
    unique_datasets = sorted(df["dataset_name"].unique())
    offset_step = 1 / max(len(unique_datasets) - 1, 1)
    offset_map = {d: -0.3 + i * offset_step for i, d in enumerate(unique_datasets)}

    palette = plt.get_cmap("tab10")
    dataset_colors = {d: palette(i) for i, d in enumerate(unique_datasets)}

    # Plot
    plt.figure(figsize=(22, 8))
    spacing = 2

    for _, row in df.iterrows():
        x_base = model_to_x[row["model"]] * spacing
        x = x_base + offset_map[row["dataset_name"]]
        color = dataset_colors[row["dataset_name"]]

        plt.errorbar(
            x=x,
            y=row["accuracy"],
            yerr=[[row["ci_minus"]], [row["ci_plus"]]],
            fmt='o',
            color=color,
            ecolor=color,
            capsize=5,
            markeredgewidth=1.5
        )

    # Eixo X
    x_ticks = [i * spacing for i in range(len(model_order))]
    plt.xticks(ticks=x_ticks, labels=model_order, rotation=25, ha="right", fontsize=16)
    plt.xlabel("Model", fontsize=18)
    plt.ylabel("Accuracy (%)", fontsize=18)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    # Legenda
    handles = [plt.Line2D([0], [0], color=dataset_colors[d], marker='o', linestyle='', markersize=10) for d in unique_datasets]
    plt.legend(
        handles, unique_datasets,
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=len(unique_datasets),
        frameon=False,
        fontsize=16
    )
    plt.tick_params(axis='y', labelsize=16)

    plt.tight_layout()
    output_path = os.path.join("./", "confidence_interval_plot.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"✅ Confidence interval plot saved to {output_path}")



def generate_bar_charts(df):
    """Generates bar plots for model accuracy, precision, recall"""
    output_dir = "./"
    sns.set(style="whitegrid")

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="dataset_name", y="accuracy", hue="model_name", data=df, palette="Set2")

    # Add values on top of bars
    for p in ax.patches:
        height = p.get_height()
        if pd.notna(height):
            ax.annotate(f"{height:.1f}",
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=10, color='black',
                        xytext=(0, 3), textcoords='offset points')

    plt.xlabel("Dataset Name", fontsize=12)
    plt.ylabel("Accuracy (%)", fontsize=12)
    plt.title("Model Accuracy Across Datasets", fontsize=14)
    plt.legend(title="LLM Model")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "accuracy_comparison.png"))
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
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed

    # Create the bar plot
    ax = sns.barplot(
        x='model',
        y='accuracy',
        hue='model',
        data=avg_accuracy_df,
        palette='viridis',
        dodge=False
    )

    # Add the average accuracy value on top of each bar
    for p in ax.patches:
        height = p.get_height()
        if pd.notna(height):  # Check if height is NaN before annotating
            ax.annotate(f'{height:.1f}',  # Format to one decimal place
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=14, color='black',
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords='offset points')

    # Formatting
    plt.xlabel("Model", fontsize=15)
    plt.ylabel("Average Accuracy (%) Across All Datasets", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=15)  # Rotate labels if they overlap
    plt.ylim(0, 105)  # Set y-axis limit slightly above 100%
    plt.tight_layout()  # Adjust layout to prevent labels overlapping

    # Save the plot
    output_path = os.path.join("./", "average_accuracy_per_model.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Average accuracy per model chart saved as {output_path}")


def generate_dataset_bar_chart(df):
    """Generates a grouped bar chart showing model performance across datasets with values on top of bars."""

    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="model", y="accuracy", hue="dataset_name", data=df, palette="Set1")

    for p in ax.patches:
        height = p.get_height()
        if pd.notna(height) and height > 0:
            ax.annotate(f"{height:.0f}",
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=9, color="black",
                        xytext=(0, 3), textcoords='offset points')

    plt.ylabel("Accuracy (%)", fontsize=15)
    plt.xlabel("", fontsize=15)
    plt.xticks(rotation=15, ha="center", fontsize=15)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
        frameon=False,
        fontsize=14
    )
    plt.tight_layout()
    output_path = os.path.join("./", "dataset_performance_chart.png")
    plt.savefig(output_path, bbox_inches="tight")
    print(f"Bar chart saved as {output_path}")


def generate_execution_time_chart(df):
    """Gera gráfico de barras com o tempo de execução dos testes por modelo e dataset."""

    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x="model", y="duration_seconds", hue="dataset_name", data=df, palette="Set2")

    for p in ax.patches:
        height = p.get_height()
        if pd.notna(height) and height > 0:
            ax.annotate(f"{height:.0f}",
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=9, color="black",
                        xytext=(0, 3), textcoords='offset points')

    plt.ylabel("Duration (seconds)", fontsize=15)
    plt.xlabel("", fontsize=15)
    plt.xticks(rotation=15, ha="center", fontsize=15)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
        frameon=False,
        fontsize=14
    )
    plt.tight_layout()
    output_path = os.path.join("./", "execution_time_chart.png")
    plt.savefig(output_path)
    plt.close()
    print(f"Execution time chart saved as {output_path}")


def generate_metrics_table(df):
    """
    Gera uma tabela com: Accuracy, Execution Time e Intervalo de Confiança (±) por modelo e dataset.
    Exporta para CSV e imprime no terminal.
    """
    if df.empty:
        print("DataFrame está vazio. Nenhuma tabela gerada.")
        return

    summary = []

    for _, row in df.iterrows():
        acc = row["accuracy"]
        dur = row["duration_seconds"]
        ci_low = row.get("confidence_interval_low")
        ci_high = row.get("confidence_interval_high")

        # Cálculo da margem ± para exibir estilo LLM Arena
        if pd.notna(ci_low) and pd.notna(ci_high) and pd.notna(acc):
            margin_plus = ci_high - acc
            margin_minus = acc - ci_low
            ci_display = f"+{margin_plus:.1f}/-{margin_minus:.1f}"
        else:
            ci_display = "N/A"

        summary.append([
            row["model"],
            row["dataset_name"],
            f"{acc:.2f}" if pd.notna(acc) else "N/A",
            f"{dur:.2f}" if pd.notna(dur) else "N/A",
            ci_display
        ])

    headers = ["Model", "Dataset", "Accuracy (%)", "Execution Time (s)", "95% CI (±)"]

    # Export to CSV
    df_summary = pd.DataFrame(summary, columns=headers)
    df_summary.to_csv("model_metrics_summary.csv", index=False)
    print("Tabela de métricas salva como 'model_metrics_summary.csv'\n")

    # Print preview in terminal
    print(tabulate(summary, headers=headers, tablefmt="grid"))


def generate_execution_time_heatmap(df):
    """
    Gera um heatmap com os tempos de execução (em segundos) para cada modelo em cada dataset.
    """
    if df.empty:
        print("DataFrame vazio. Heatmap não gerado.")
        return

    pivot_df = df.pivot_table(
        index="model",
        columns="dataset_name",
        values="duration_seconds",
        aggfunc="mean",
    )

    # Ordena por tempo médio de execução total
    pivot_df["Avg"] = pivot_df.mean(axis=1)
    pivot_df = pivot_df.sort_values(by="Avg", ascending=False).drop(columns="Avg")

    plt.figure(figsize=(12, 6))
    sns.heatmap(
        pivot_df,
        annot=True,
        fmt=".0f",
        cmap="YlGnBu",
        linewidths=0.5,
        cbar_kws={"label": "Duration (s)"},
        annot_kws={"size": 14}
    )

    plt.tick_params(axis='y', labelsize=14)
    plt.tick_params(axis='x', labelsize=14)
    plt.xlabel("Dataset", fontsize=16)
    plt.ylabel("Model", fontsize=16)
    plt.xticks(rotation=25, ha='right')
    plt.tight_layout()

    output_path = os.path.join("./", "execution_time_heatmap.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Heatmap saved as {output_path}")


def main():
    print("Starting LLM Model Evaluation...")

    results = evaluate_models()
    df = save_results(results)

    #df = pd.read_csv("evaluation_results.csv")

    generate_bar_charts(df)
    generate_average_accuracy_chart(df)
    generate_dataset_bar_chart(df)
    generate_execution_time_chart(df)
    generate_confidence_interval_plot(df)
    generate_execution_time_heatmap(df)
    generate_metrics_table(df)

    print("Evaluation process completed successfully!")


if __name__ == "__main__":
    main()
