from django.db import migrations
import pandas as pd
import os


def load_initial_data(apps, schema_editor):
    """
    Load all datasets from CSV files located in the 'fixtures' directory.
    """
    csv_dir = os.path.join(os.path.dirname(__file__), "..", "fixtures")
    # Get all CSV files in the directory
    csv_files = [file for file in os.listdir(csv_dir) if file.endswith(".csv")]

    Dataset = apps.get_model("api", "Dataset")
    Question = apps.get_model("api", "Question")
    LLMModel = apps.get_model("api", "LLMModel")

    if not csv_files:
        print("No CSV files found in the fixtures directory.")
        return

    for filename in csv_files:
        csv_path = os.path.join(csv_dir, filename)

        dataset_name = filename.replace("_", " ").replace(".csv", "").title()  # Format dataset name
        dataset, created = Dataset.objects.get_or_create(name=dataset_name)

        try:
            df = pd.read_csv(csv_path, sep=';', skiprows=1)
            df.columns = df.columns.str.strip()
            questions = []

            # Convert DataFrame rows into Question objects
            for index, row in df.iterrows():
                question = Question(
                    dataset=dataset,
                    question=row["Question"],
                    option_a=row["Option A"].strip(),
                    option_b=row["Option B"].strip(),
                    option_c=row["Option C"].strip(),
                    option_d=row["Option D"].strip(),
                    correct_option=row["Correct Answer"].strip(),
                    difficulty=row["Difficulty"].strip(),
                    domain=row["Domain"],
                    explanation=row["Explanation"]
                )
                questions.append(question)

            # Bulk insert for performance
            Question.objects.bulk_create(questions)
            print(f" Successfully loaded {len(questions)} questions into '{dataset_name}' dataset.")

        except Exception as e:
            print(f"Error loading questions in dataset {dataset_name}: {e}")

    # Load initial LLM models data
    llm_models = [
        {"provider": "Mistral AI", "name": "Mistral 7B", "model": "accounts/fireworks/models/mistral-7b",
         "api_url": "https://api.fireworks.ai/inference/v1/chat/completions"},
        {"provider": "Mistral AI", "name": "Mixtral 8x22B", "model": "accounts/fireworks/models/mixtral-8x22b-instruct",
         "api_url": "https://api.fireworks.ai/inference/v1/chat/completions"},
    ]

    LLMModel.objects.bulk_create([LLMModel(**llm) for llm in llm_models])


def delete_data(apps, schema_editor):
    """Deletes all datasets and questions and LLM models (reverse operation)."""
    Dataset = apps.get_model("api", "Dataset")
    Question = apps.get_model("api", "Question")
    LLMModel = apps.get_model("api", "LLMModel")

    Question.objects.all().delete()
    Dataset.objects.all().delete()
    LLMModel.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data, delete_data)
    ]
