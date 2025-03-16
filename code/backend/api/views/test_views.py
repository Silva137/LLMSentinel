import asyncio
from collections import Counter
import numpy as np
import openai
import regex as re
from asgiref.sync import async_to_sync, sync_to_async
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Test, QuestionResult
from ..serializers.question_serializer import QuestionResultSerializer
from ..serializers.test_serializer import TestSerializer, TestCreationSerializer
from sklearn.metrics import classification_report
import time
import random

client = openai.AsyncOpenAI(
        api_key="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",
        base_url="https://openrouter.ai/api/v1"
    )


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Override default GET to return only tests of the authenticated user.
        Supports filtering by dataset_id and llm_model_name.
        """
        queryset = Test.objects.filter(user=self.request.user)

        dataset_name = self.request.query_params.get("dataset_name")
        llm_model_name = self.request.query_params.get("llm_model_name")

        if dataset_name:
            queryset = queryset.filter(dataset__name=dataset_name)

        if llm_model_name:
            queryset = queryset.filter(llm_model__name=llm_model_name)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Override default POST to evaluate the dataset with a specific LLM model and compute test metrics.
        """
        serializer = TestCreationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            test = serializer.save()
            async_to_sync(evaluate_llm)(test)
            test.completed_at = timezone.now()

            compute_test_metrics(test)

            response_serializer = TestSerializer(test)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # igual a get test ??? nsei se é necessario
    @action(detail=True, methods=['get'])
    def results(self, request, pk):
        """
        Get all question results for a specific test.
        """
        test = get_object_or_404(Test, id=pk, user=request.user)
        results = QuestionResult.objects.filter(test=test)
        serializer = QuestionResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


async def evaluate_llm(test):
    """
    Runs the LLM model evaluation on all questions from the dataset.
    """

    semaphore = asyncio.Semaphore(3)

    async def limited_query(question, llm_model):
        async with semaphore:
            return await query_llm(llm_model, question)

    try:
        questions = await sync_to_async(list)(test.dataset.questions.all())
        llm_model = test.llm_model

        tasks = [limited_query(question, llm_model) for question in questions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        q_results = []
        for question, result in zip(questions, results):
            answer, explanation, confidence = result

            correct = (answer.strip().upper() == question.correct_option.strip().upper())
            # Create each QuestionResult in the database (this part remains synchronous)
            q_results.append(QuestionResult(
                test=test,
                question=question,
                answer=answer,
                explanation=explanation,
                correct=correct,
                response_time=0.5,
                confidence=confidence
            ))

        await sync_to_async(QuestionResult.objects.bulk_create)(q_results)

    except Exception as e:
        print(f"Error occurred during evaluation: {e}")


async def query_llm(llm_model, question):
    """
    Sends the question to the LLM model and retrieves the response.
    """

    prompt = (
        f"You are a cybersecurity expert. Analyze the following multiple-choice question and strictly follow the response format:\n\n"
        f"Question:\n{question.question}\n\n"
        f"Options:\n"
        f"A: {question.option_a}\n"
        f"B: {question.option_b}\n"
        f"C: {question.option_c}\n"
        f"D: {question.option_d}\n\n"
        f"### Important Instructions:\n"
        f"- Your response **must** strictly follow the given format.\n"
        f"- Always include 'Answer: ' followed by the correct letter (A, B, C, or D).\n"
        f"- Always include 'Explanation: ' followed by a brief justification.\n"
        f"- Always include 'Confidence: ' followed by a number between 0.0 and 1.0, representing your certainty in your answer.\n"
        f"- Do not respond in free text or change the format.\n\n"
        f"### Expected Response Format:\n"
        f"Answer: <Correct answer letter (A, B, C, or D)>\n"
        f"Explanation: <Brief explanation for the chosen answer>\n"
        f"Confidence: <A float between 0.0 and 1.0>\n\n"
        f"### Example Response:\n"
        f"Answer: C\n"
        f"Explanation: Option C is correct because ...\n"
        f"Confidence: 0.85"
    )

    try:
        response = await client.chat.completions.create(
            model=llm_model.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

        content = response.choices[0].message.content

        # Use regex to extract answer and explanation
        answer_match = re.search(r"Answer:\s*([A-D])", content, re.IGNORECASE)
        explanation_match = re.search(r"Explanation:\s*(.*)", content, re.IGNORECASE)
        confidence_match = re.search(r"Confidence:\s*([0-1]\.\d+|1|0)", content, re.IGNORECASE)

        # Extract values safely
        answer = answer_match.group(1).strip().upper() if answer_match else "X"
        explanation = explanation_match.group(1).strip() if explanation_match else "Explanation not found."
        confidence = float(confidence_match.group(1)) if confidence_match else 0.0

        return answer, explanation, confidence

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return "X", "An unexpected error occurred while querying the LLM.", 0.0



async def query_llm_with_retry(llm_model, question, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            return await query_llm(llm_model, question)
        except Exception as e:
            if "Capacity temporarily exceeded" in str(e) and retries < max_retries - 1:
                # Exponential backoff with jitter
                sleep_time = (2 ** retries) + random.random()
                print(f"Capacity exceeded. Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                retries += 1
            else:
                raise




def compute_test_metrics(test):
    """
    Computes the test metrics.
    """
    results = QuestionResult.objects.filter(test=test)

    # Extract correct answers and predicted answers, filtering out 'X' (failed queries)
    y_true = [res.question.correct_option for res in results if res.answer != "X"]
    y_pred = [res.answer for res in results if res.answer != "X"]
    confidences = [res.confidence for res in results if res.answer != "X"]

    # General test statistics
    test.total_questions = len(results)
    test.correct_answers = sum(1 for i in range(len(y_true)) if y_true[i] == y_pred[i])
    test.accuracy_percentage = (test.correct_answers / len(y_true) * 100) if len(y_true) > 0 else 0
    test.failed_queries = sum(1 for res in results if res.answer == "X")

    # Compute Precision, Recall, and F1-score for each class (A, B, C, D)
    class_metrics = {}
    if y_true and y_pred:
        classification_metrics = classification_report(y_true, y_pred, labels=['A', 'B', 'C', 'D'], output_dict=True)

        for option in ['A', 'B', 'C', 'D']:
            class_metrics[option] = {
                "precision": classification_metrics.get(option, {}).get("precision", 0),
                "recall": classification_metrics.get(option, {}).get("recall", 0),
                "f1-score": classification_metrics.get(option, {}).get("f1-score", 0),
            }

        # Store class-based metrics as JSON
        test.class_metrics = class_metrics

        # Store macro average metrics
        test.precision_avg = classification_metrics["macro avg"]["precision"]
        test.recall_avg = classification_metrics["macro avg"]["recall"]
        test.f1_avg = classification_metrics["macro avg"]["f1-score"]

        # Store answer distribution as JSON
        test.answer_distribution = dict(Counter([res.answer for res in results]))

        # 1. Compute Average Confidence Score
        test.avg_confidence = np.mean(confidences) if confidences else 0.0

        # 2. Compute **Confidence-Weighted Accuracy (with penalties for incorrect answers)**
        weighted_score = sum(
            confidences[i] * (1 if y_true[i] == y_pred[i] else -1)  # Penalize incorrect answers
            for i in range(len(y_true))
        )
        test.confidence_weighted_accuracy = (weighted_score / sum(confidences)) * 100 if sum(confidences) > 0 else 0.0



    test.save()
