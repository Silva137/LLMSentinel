import io

import pandas as pd
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from ..models import Dataset, Question
from ..serializers.dataset_serializer import DatasetSerializer, DatasetUploadSerializer
from rest_framework.response import Response


"""
    ViewSet for managing Datasets.

    Routes:
    - GET    /api/datasets/         → List all datasets
    - POST   /api/datasets/         → Create a new dataset
    - GET    /api/datasets/{id}/    → Retrieve a specific dataset by ID
    - PUT    /api/datasets/{id}/    → Update a dataset (full update)
    - PATCH  /api/datasets/{id}/    → Partially update a dataset
    - DELETE /api/datasets/{id}/    → Delete a dataset
"""


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        is_public = self.request.query_params.get('is_public')

        if is_public == 'true':
            return Dataset.objects.filter(is_public=True)
        elif is_public == 'false':
            return Dataset.objects.filter(is_public=False, owner=user)
        else:
            return Dataset.objects.filter(Q(owner=user) | Q(owner=None))

    @action(detail=True, methods=['post'], url_path='share')
    def share_dataset(self, request, pk=None):
        """
        Make the dataset public.
        """
        try:
            dataset = self.get_object()

            if dataset.owner is None:
                return Response({"detail": "Cannot share a default dataset."},
                                status=status.HTTP_400_BAD_REQUEST)

            if dataset.owner != request.user:
                return Response({"detail": "You do not have permission to share this dataset."},
                                status=status.HTTP_403_FORBIDDEN)

            dataset.is_public = True
            dataset.save()

            return Response({"detail": "Dataset successfully shared with the community."}, status=status.HTTP_200_OK)

        except Dataset.DoesNotExist:
            return Response({"detail": "Dataset not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def upload(self, request):
        """
        Endpoint to upload a CSV file and create a new dataset.
        """

        print("Request Data:", request.data)  # <-- Adiciona log para debug
        print("Request Files:", request.FILES)  # <-- Verifica se o arquivo está presente

        serializer = DatasetUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dataset_name = request.data['name']
        dataset_description = request.data['description'] if 'description' in request.data else "No description provided"
        file = request.FILES['file']
        user = request.user

        try:
            file.seek(0)  # Reset file pointer
            file_content = io.BytesIO(file.read())

            dataset = pd.read_csv(file_content, sep=';', skiprows=1)
            dataset_obj = Dataset.objects.create(name=dataset_name, description=dataset_description, owner=user)
            questions = []

            # Convert DataFrame rows into Question objects
            for index, row in dataset.iterrows():
                question = Question(
                    dataset=dataset_obj,
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

            return Response(
                {"message": f"Dataset '{dataset_name}' created successfully with {len(questions)} questions."},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response({"error": f"Error processing CSV file {dataset_name} : {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
