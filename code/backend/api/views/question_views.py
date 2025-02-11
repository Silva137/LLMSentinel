from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from ..models import Question, QuestionResult, Test
from ..serializers.question_serializer import QuestionSerializer, QuestionResultSerializer
from rest_framework.response import Response


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class QuestionResultViewSet(viewsets.ModelViewSet):
    queryset = QuestionResult.objects.all()
    serializer_class = QuestionResultSerializer
    permission_classes = [IsAuthenticated]



