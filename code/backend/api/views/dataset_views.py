from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Dataset
from ..serializers.dataset_serializer import DatasetSerializer

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


