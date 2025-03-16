import openai
from django.db import migrations
import pandas as pd
import os
import requests


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
                    difficulty=row.get("Difficulty", "").strip() or None,
                    domain=row.get("Domain", "").strip() or None,
                    explanation=row.get("Explanation", "").strip() or None,
                )
                questions.append(question)

            # Bulk insert for performance
            Question.objects.bulk_create(questions)
            print(f" Successfully loaded {len(questions)} questions into '{dataset_name}' dataset.")

        except Exception as e:
            print(f"Error loading questions in dataset {dataset_name}: {e}")

    client = openai.OpenAI(
        api_key="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",
        base_url="https://openrouter.ai/api/v1"
    )

    try:
        response = client.models.list()
        models = getattr(response, "data", [])

        llm_models = []
        for model in models:
            model_id = model.id
            name = getattr(model, "name", "")
            provider = model_id.split("/")[0] if "/" in model_id else "Unknown"
            description = getattr(model, "description", "")

            llm_models.append(
                LLMModel(
                    model_id=model_id,
                    name=name,
                    provider=provider,
                    description=description
                )
            )

        LLMModel.objects.bulk_create(llm_models, ignore_conflicts=True)
        print(f"Successfully added {len(llm_models)} LLM models from OpenRouter.")

    except openai.OpenAIError as e:
        print(f"Error fetching LLM models from OpenRouter: {e}")


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
