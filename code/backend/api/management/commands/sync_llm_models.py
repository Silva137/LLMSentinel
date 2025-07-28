from django.core.management.base import BaseCommand
import openai
from api.models import LLMModel


class Command(BaseCommand):
    help = "Sync LLM models from OpenRouter to the database."

    def handle(self, *args, **kwargs):
        client = openai.OpenAI(
            api_key="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",
            base_url="https://openrouter.ai/api/v1"
        )

        try:
            # Fetch models from OpenRouter
            response = client.models.list()
            models = getattr(response, "data", [])

            # Extract model IDs from OpenRouter
            openrouter_ids = {model.id for model in models}

            # Fetch existing model IDs from the database
            existing_models = LLMModel.objects.all()
            existing_ids = set(existing_models.values_list("model_id", flat=True))

            # Identify models to remove (exist in DB but not in OpenRouter)
            models_to_remove = existing_models.filter(model_id__in=(existing_ids - openrouter_ids))
            removed_model_names = [model.name for model in models_to_remove]
            models_to_remove.delete()

            # Identify new models to add
            new_models = []
            added_model_names = []
            for model in models:
                if model.id in existing_ids:
                    continue  # Skip if already exists

                name = getattr(model, "name", "")
                provider = model.id.split("/")[0] if "/" in model.id else "Unknown"
                description = getattr(model, "description", "")

                new_models.append(
                    LLMModel(
                        model_id=model.id,
                        name=name,
                        provider=provider,
                        description=description,
                    )
                )
                added_model_names.append(name)

            # Bulk create new models
            LLMModel.objects.bulk_create(new_models)

            # Print results
            self.stdout.write(self.style.SUCCESS(
                f"Successfully synced models. Added {len(new_models)} new models and removed {len(models_to_remove)} old models."
            ))
            if added_model_names:
                self.stdout.write(self.style.SUCCESS(f"Added models: {', '.join(added_model_names)}"))
            if removed_model_names:
                self.stdout.write(self.style.WARNING(f"Removed models: {', '.join(removed_model_names)}"))

        except openai.OpenAIError as e:
            self.stderr.write(self.style.ERROR(f"Error fetching LLM models: {e}"))