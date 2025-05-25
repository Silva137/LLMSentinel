from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Question, QuestionResult
from ..serializers.question_serializer import QuestionSerializer, QuestionResultSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='dataset/(?P<dataset_id>[^/.]+)')
    def questions_by_dataset(self, request, dataset_id=None):
        queryset = self.queryset.filter(dataset_id=dataset_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class QuestionResultViewSet(viewsets.ModelViewSet):
    queryset = QuestionResult.objects.all()
    serializer_class = QuestionResultSerializer
    permission_classes = [IsAuthenticated]



