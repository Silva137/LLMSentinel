import csv
from django.core.management.base import BaseCommand
from ...models import Dataset, Question


class Command(BaseCommand):
    help = 'Load datasets and questions from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('dataset_csv', type=str, help='Path to the dataset CSV file')
        parser.add_argument('questions_csv', type=str, help='Path to the questions CSV file')

    def handle(self, *args, **kwargs):
        dataset_csv = kwargs['dataset_csv']
        questions_csv = kwargs['questions_csv']

        # Load datasets
        with open(dataset_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Dataset.objects.create(
                    name=row['name'],
                    description=row.get('description', '')
                )

        # Load questions
        with open(questions_csv, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dataset = Dataset.objects.get(name=row['dataset_name'])
                Question.objects.create(
                    dataset=dataset,
                    question=row['question'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'],
                    option_d=row['option_d'],
                    correct_option=row['correct_option'],
                    difficulty=row['difficulty'],
                    domain=row['domain'],
                    explanation=row.get('explanation', '')
                )

        self.stdout.write(self.style.SUCCESS('Successfully loaded datasets and questions from CSV files'))
