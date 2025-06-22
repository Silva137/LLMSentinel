from django.db.models import Avg, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
        by the authenticated user.
        """
        user = request.user
        model_ids_str = request.query_params.get('model_ids', '')

        if not model_ids_str:
            return Response({"error": "No model_ids provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            model_ids = [int(id_str) for id_str in model_ids_str.split(',') if id_str.isdigit()]
            if not model_ids:
                return Response({"error": "Invalid or empty model_ids provided."},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Model IDs must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        # Count how many of the selected models have been used per dataset
        dataset_counts = (
            Test.objects
            .filter(user=user, llm_model_id__in=model_ids)
            .values('dataset_id')
            .annotate(model_count=Count('llm_model', distinct=True))
            .filter(model_count=len(model_ids))  # Only datasets tested with all selected models
            .values_list('dataset_id', flat=True)
        )

        datasets = Dataset.objects.filter(id__in=dataset_counts).values('id', 'name')
        data = [{'id': str(dataset['id']), 'name': dataset['name']} for dataset in datasets]
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='models-performance-on-dataset')
    def get_models_performance_on_dataset(self, request):
        """
        Returns details of the most recent completed test for selected models on a specific dataset,
        for tests run by the authenticated user.
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
            # Fetch the most recent completed test for the given model and dataset
            latest_test = Test.objects.filter(
                user=user,
                llm_model_id=model_id,
                dataset_id=dataset_id,
                started_at__isnull=False,
                completed_at__isnull=False
            ).order_by('-completed_at').first()  # Get the most recent test

            if latest_test:
                model_instance = LLMModel.objects.get(id=model_id)
                dataset_instance = Dataset.objects.get(id=dataset_id)
                results.append({
                    'modelId': str(model_id),
                    'modelName': model_instance.name,
                    'datasetId': str(dataset_id),
                    'datasetName': dataset_instance.name,
                    'accuracyPercentage': latest_test.accuracy_percentage if latest_test.accuracy_percentage is not None else None,
                    'startedAt': latest_test.started_at.isoformat() if latest_test.started_at else None,
                    'completedAt': latest_test.completed_at.isoformat() if latest_test.completed_at else None,
                })

        return Response(results, status=status.HTTP_200_OK)
