import json
import requests
import regex as re
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Test, QuestionResult
from ..serializers.question_serializer import QuestionResultSerializer
from ..serializers.test_serializer import TestSerializer, TestCreationSerializer


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override default GET to return only tests of the authenticated user.
        """
        return Test.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override default POST to evaluate the dataset with a specific LLM model and compute test metrics.
        """
        serializer = TestCreationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            test = serializer.save()
            evaluate_llm(test)
            test.completed_at = timezone.now()

            compute_test_metrics(test)

            response_serializer = TestSerializer(test)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def results(self, request, pk):
        """
        Get all question results for a specific test.
        """
        test = get_object_or_404(Test, id=pk, user=request.user)
        results = QuestionResult.objects.filter(test=test)
        serializer = QuestionResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def evaluate_llm(test):
    """
    Runs the LLM model evaluation on all questions from the dataset.
    """
    questions = test.dataset.questions.all()
    llm_model = test.llm_model

    for question in questions:
        answer, explanation = query_llm(llm_model, question)

        correct = (answer.strip().upper() == question.correct_option.strip().upper())

        QuestionResult.objects.create(
            test=test,
            question=question,
            answer=answer,
            explanation=explanation,
            correct=correct,
            response_time=0.5
        )


def  query_llm(llm_model, question):
    """
    Sends the question to the LLM model and retrieves the response.
    """
    url = llm_model.api_url
    model = llm_model.model
    prompt = (
        f"You are a cybersecurity expert. Analyze the following multiple-choice question:\n\n"
        f"Question: {question.question}\n"
        f"Options:\n"
        f"A: {question.option_a}\n"
        f"B: {question.option_b}\n"
        f"C: {question.option_c}\n"
        f"D: {question.option_d}\n\n"
        f"Respond strictly in the following format:\n"
        f"Answer: <Correct answer letter (A, B, C, or D)>\n"
        f"Explanation: <Brief explanation for the chosen answer>\n\n"
        f"Example response:\n"
        f"Answer: C\n"
        f"Explanation: Option C is correct because ..."
    )

    payload = {
        "model": model,
        "max_tokens": 500,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer fw_3ZjJEBdGSgYneU2XaMMeFn2w"  # Include in model ??
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Check for request errors
        content = response.json()["choices"][0]["message"]["content"]

        # Use regex to extract answer and explanation
        answer_match = re.search(r"Answer:\s*([A-D])", content, re.IGNORECASE)
        explanation_match = re.search(r"Explanation:\s*(.*)", content, re.IGNORECASE)

        # Extract values safely
        answer = answer_match.group(1).strip().upper() if answer_match else "N/A"
        explanation = explanation_match.group(1).strip() if explanation_match else "Explanation not found."

        return answer, explanation

    except requests.exceptions.RequestException as e:
        return f"Error querying Fireworks LLM: {e}"


def compute_test_metrics(test):
    """
    Computes the test metrics (correct answers and accuracy percentage).
    """
    results = QuestionResult.objects.filter(test=test)

    test.total_questions = results.count()
    test.correct_answers = results.filter(correct=True).count()
    test.accuracy_percentage = (test.correct_answers / test.total_questions) * 100

    test.save()
