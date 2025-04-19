from django.core.management.base import BaseCommand
from api.models import LLMModel
import openai

class Command(BaseCommand):
    help = "Sync LLM models from OpenRouter to the database."

    def handle(self, *args, **kwargs):
        client = openai.OpenAI(
            api_key="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",
            base_url="https://openrouter.ai/api/v1"
        )

        try:
            response = client.models.list()
            models = getattr(response, "data", [])

            existing_ids = set(LLMModel.objects.values_list("model_id", flat=True))

            new_models = []
            for model in models:
                model_id = model.id
                if model_id in existing_ids:
                    continue  # Ignora se já existir

                name = getattr(model, "name", "")
                provider = model_id.split("/")[0] if "/" in model_id else "Unknown"
                description = getattr(model, "description", "")

                new_models.append(
                    LLMModel(
                        model_id=model_id,
                        name=name,
                        provider=provider,
                        description=description
                    )
                )

            LLMModel.objects.bulk_create(new_models)
            self.stdout.write(self.style.SUCCESS(f"Successfully added {len(new_models)} new LLM models from OpenRouter."))

        except openai.OpenAIError as e:
            self.stderr.write(self.style.ERROR(f"Error fetching LLM models: {e}"))
