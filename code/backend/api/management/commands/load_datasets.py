import os
import pandas as pd
from django.core.management.base import BaseCommand
from api.models import Dataset, Question

# Dataset descriptions
DESCRIPTIONS = {
    "applications security": "Dataset from CyberDomain covering key cybersecurity topics.",
    "cloud security": "Dataset from CyberDomain covering key cybersecurity topics.",
    "cryptography": "Dataset from CyberDomain covering key cybersecurity topics.",
    "iam": "Dataset from CyberDomain covering key cybersecurity topics.",
    "network security": "Dataset from CyberDomain covering key cybersecurity topics.",
    "operating systems security": "Dataset from CyberDomain covering key cybersecurity topics.",
    "digital forensics": "Dataset from CyberDomain covering key cybersecurity topics.",

    "honeypots": "CSLU dataset focused on honeypot concepts and detection.",
    "ctf": "CSLU dataset with Capture The Flag style security questions.",
    "malware": "CSLU dataset about malware concepts, analysis and threats.",

    "secqa v1": "SecQA V1 dataset with 110 basic multiple-choice security questions.",
    "secqa v2": "SecQA V2 dataset with 100 more advanced multiple-choice security questions.",

    "secmmlu": "CyberBench dataset with 100 cybersecurity questions derived from MMLU.",
    "cyquiz": "CyberBench dataset with 100 practice-oriented cybersecurity questions.",
}


class Command(BaseCommand):
    help = "Load all datasets from CSV files located in the 'fixtures' directory, skipping existing datasets."

    def handle(self, *args, **kwargs):
        csv_dir = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")

        if not os.path.exists(csv_dir):
            self.stdout.write(self.style.WARNING(f"Fixtures directory not found: {csv_dir}"))
            return

        csv_files = [file for file in os.listdir(csv_dir) if file.endswith(".csv")]

        if not csv_files:
            self.stdout.write(self.style.WARNING("No CSV files found in the fixtures directory."))
            return

        for filename in csv_files:
            csv_path = os.path.join(csv_dir, filename)
            dataset_name = filename.replace("_", " ").replace(".csv", "").title()
            dataset_key = dataset_name.strip().lower()

            if Dataset.objects.filter(name=dataset_name).exists():
                self.stdout.write(self.style.WARNING(
                    f"Dataset '{dataset_name}' already exists. Skipping."
                ))
                continue

            description = DESCRIPTIONS.get(dataset_key, "")
            dataset = Dataset.objects.create(name=dataset_name, description=description)

            try:
                df = pd.read_csv(csv_path, sep=';', skiprows=1)
                df.columns = df.columns.str.strip()
                questions = []

                for _, row in df.iterrows():
                    question = Question(
                        dataset=dataset,
                        question=row["Question"].strip(),
                        option_a=row["Option A"].strip(),
                        option_b=row["Option B"].strip(),
                        option_c=row["Option C"].strip(),
                        option_d=row["Option D"].strip(),
                        correct_option=row["Correct Answer"].strip(),
                    )
                    questions.append(question)

                Question.objects.bulk_create(questions)
                self.stdout.write(self.style.SUCCESS(
                    f"Loaded {len(questions)} questions into new dataset '{dataset_name}'."
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error loading '{dataset_name}': {e}"))
                dataset.delete()  # Clean up if there's an error
