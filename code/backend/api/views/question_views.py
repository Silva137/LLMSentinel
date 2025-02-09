from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Question, QuestionResult
from ..serializers.question_serializer import QuestionSerializer, QuestionResultSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class QuestionResultViewSet(viewsets.ModelViewSet):
    queryset = QuestionResult.objects.all()
    serializer_class = QuestionResultSerializer
    permission_classes = [IsAuthenticated]

