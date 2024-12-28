from django.core.management.base import BaseCommand
from ...models import LLMModel


class Command(BaseCommand):
    help = 'Load initial LLM models data'

    def handle(self, *args, **kwargs):
        # Define the data to load
        data = [
            {"name": "GPT", "model": "4.0", "api_url": "https://api.openai.com/v1/gpt-4"},
            {"name": "Gemini", "model": "1.5", "api_url": "https://api.google.com/v1/gemini-1.5"},
        ]

        # Load the data into the LLMModel table
        for entry in data:
            LLMModel.objects.create(**entry)

        self.stdout.write(self.style.SUCCESS('Successfully loaded initial LLM models data'))
