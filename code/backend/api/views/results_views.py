from django.db.models import Avg, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from statsmodels.stats.proportion import proportion_confint

from ..models import Test, LLMModel, Dataset, QuestionResult


class ResultsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='tested-models')
    def get_tested_models(self, request):
        """
        Returns a list of unique LLM Models that have at least one test result
        associated with the authenticated user.
        """
        user = request.user
        # Get LLMModels that are present in the Test table for the current user
        tested_model_ids = Test.objects.filter(user=user) \
            .values_list('llm_model_id', flat=True) \
            .distinct()

        models = LLMModel.objects.filter(id__in=tested_model_ids).values('id', 'name')

        # Convert model_id to string 'id' for consistency with frontend expectations if needed
        # Or ensure your frontend SelectableModel uses 'id' as a string if pk is int
        data = [{'id': str(model['id']), 'name': model['name']} for model in models]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='available-datasets')
    def get_available_datasets_for_models(self, request):
        """
        Returns datasets that have been tested with ALL of the selected models
        by the authenticated user. If no models are provided, returns all datasets
        that have been tested by the user.
        """
        user = request.user
        model_ids_str = request.query_params.get('model_ids', '')

        try:
            model_ids = [int(id_str) for id_str in model_ids_str.split(',') if id_str.isdigit()]
        except ValueError:
            return Response({"error": "Model IDs must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        if model_ids:
            # Count how many of the selected models have been used per dataset
            dataset_ids = (
                Test.objects
                .filter(user=user, llm_model_id__in=model_ids)
                .values('dataset_id')
                .annotate(model_count=Count('llm_model', distinct=True))
                .filter(model_count=len(model_ids))  # Only datasets tested with all selected models
                .values_list('dataset_id', flat=True)
            )
        else:
            # No model_ids: return all datasets tested by the user
            dataset_ids = (
                Test.objects
                .filter(user=user)
                .values_list('dataset_id', flat=True)
                .distinct()
            )

        datasets = Dataset.objects.filter(id__in=dataset_ids).values('id', 'name')
        data = [{'id': str(dataset['id']), 'name': dataset['name']} for dataset in datasets]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='models-performance-on-dataset')
    def get_models_performance_on_dataset(self, request):
        """
        Returns the average performance of models on a given dataset,
        based on all completed tests by the authenticated user.

        Query Params:
        - model_ids: Comma-separated string of LLMModel IDs
        - dataset_id: ID of the Dataset
        """
        user = request.user
        model_ids_str = request.query_params.get('model_ids', '')
        dataset_id_str = request.query_params.get('dataset_id', '')

        if not model_ids_str or not dataset_id_str:
            return Response(
                {"error": "Missing required query parameters: model_ids and dataset_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            model_ids = [int(id_str) for id_str in model_ids_str.split(',') if id_str.isdigit()]
            dataset_id = int(dataset_id_str)
            if not model_ids:
                return Response({"error": "Invalid or empty model_ids provided."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Model IDs and Dataset ID must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        for model_id in model_ids:
            tests = Test.objects.filter(
                user=user,
                llm_model_id=model_id,
                dataset_id=dataset_id,
                started_at__isnull=False,
                completed_at__isnull=False
            )

            if tests.exists():
                executions = list(tests)
                num_executions = len(executions)

                total_accuracy = sum(t.accuracy_percentage or 0 for t in executions)
                total_duration = sum(
                    (t.completed_at - t.started_at).total_seconds()
                    for t in executions if t.completed_at and t.started_at
                )

                avg_accuracy = total_accuracy / num_executions if num_executions > 0 else None
                avg_duration = total_duration / num_executions if num_executions > 0 else None

                model_instance = LLMModel.objects.get(id=model_id)
                dataset_instance = Dataset.objects.get(id=dataset_id)

                results.append({
                    'modelId': str(model_id),
                    'modelName': model_instance.name,
                    'datasetId': str(dataset_id),
                    'datasetName': dataset_instance.name,
                    'accuracyPercentage': round(avg_accuracy, 2) if avg_accuracy is not None else None,
                    'durationSeconds': round(avg_duration, 2) if avg_duration is not None else None,
                    'numberOfExecutions': num_executions
                })

        return Response(results, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='model-average-performance-on-dataset')
    def get_model_average_performance_on_dataset(self, request):
        """
        Returns the average accuracy and execution time of all completed tests
        for a given model name and dataset name by the authenticated user.

        Query Params:
        - model_name: Name of the LLM model
        - dataset_name: Name of the Dataset
        """
        user = request.user
        model_name = request.query_params.get('model_name')
        dataset_name = request.query_params.get('dataset_name')

        if not model_name or not dataset_name:
            return Response(
                {"error": "Missing required query parameters: model_name and dataset_name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            model = LLMModel.objects.get(name=model_name)
            dataset = Dataset.objects.get(name=dataset_name)
        except LLMModel.DoesNotExist:
            return Response({"error": f"Model with name '{model_name}' not found."}, status=status.HTTP_404_NOT_FOUND)
        except Dataset.DoesNotExist:
            return Response({"error": f"Dataset with name '{dataset_name}' not found."},
                            status=status.HTTP_404_NOT_FOUND)

        tests = Test.objects.filter(
            user=user,
            llm_model=model,
            dataset=dataset,
            started_at__isnull=False,
            completed_at__isnull=False
        )

        if not tests.exists():
            return Response({"message": "No completed tests found for the given model and dataset."},
                            status=status.HTTP_200_OK)

        num_executions = tests.count()
        total_accuracy = sum(t.accuracy_percentage or 0 for t in tests)
        total_duration = sum(
            (t.completed_at - t.started_at).total_seconds()
            for t in tests if t.started_at and t.completed_at
        )

        avg_accuracy = total_accuracy / num_executions if num_executions > 0 else None
        avg_duration = total_duration / num_executions if num_executions > 0 else None

        # Calcular o IC
        all_results = QuestionResult.objects.filter(test__in=tests).exclude(answer="X")

        total_questions = all_results.count()
        total_correct = all_results.filter(correct=True).count()

        if total_questions > 0:
            ci_low, ci_high = proportion_confint(total_correct, total_questions, alpha=0.05, method="wilson")
            ci_low *= 100
            ci_high *= 100
        else:
            ci_low = ci_high = 0.0

        result = {
            "modelName": model.name,
            "datasetName": dataset.name,
            "averageAccuracyPercentage": round(avg_accuracy, 2) if avg_accuracy is not None else None,
            "averageDurationSeconds": round(avg_duration, 2) if avg_duration is not None else None,
            "confidenceIntervalLow": round(ci_low, 2) if ci_low is not None else None,
            "confidenceIntervalHigh": round(ci_high, 2) if ci_high is not None else None,
            "numberOfExecutions": num_executions
        }

        return Response(result, status=status.HTTP_200_OK)

