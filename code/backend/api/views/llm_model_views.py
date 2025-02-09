from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import LLMModel
from ..serializers.llm_serializer import LLMModelSerializer

"""
    ViewSet for managing LLM Models.

    Routes:
    - GET    /api/llm-models/         → List all LLM models
    - POST   /api/llm-models/         → Create a new LLM model
    - GET    /api/llm-models/{id}/    → Retrieve a specific LLM model by ID
    - PUT    /api/llm-models/{id}/    → Update an LLM model (full update)
    - PATCH  /api/llm-models/{id}/    → Partially update an LLM model
    - DELETE /api/llm-models/{id}/    → Delete an LLM model
"""


class LLMModelViewSet(viewsets.ModelViewSet):
    queryset = LLMModel.objects.all()
    serializer_class = LLMModelSerializer
    permission_classes = [IsAuthenticated]



