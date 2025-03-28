import asyncio
from collections import Counter
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

    @action(detail=False, methods=['delete'])
    def delete_by_llm(self, request):
        """
        Delete all tests related to a specific LLM model for the authenticated user.
        """
        llm_model_name = request.data.get("llm_model_name")

        if not llm_model_name:
            return Response({"error": "Missing required parameter: llm_model_name"}, status=status.HTTP_400_BAD_REQUEST)

        tests_to_delete = Test.objects.filter(user=request.user, llm_model__name=llm_model_name)

        if not tests_to_delete.exists():
            return Response({"message": "No tests found for the given LLM model."}, status=status.HTTP_404_NOT_FOUND)

        deleted_count, _ = tests_to_delete.delete()

        return Response({"message": f"Successfully deleted {deleted_count} tests for LLM model '{llm_model_name}'."},
                        status=status.HTTP_200_OK)


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
            answer, explanation, confidence, content = result

            correct = (answer.strip().upper() == question.correct_option.strip().upper())
            # Create each QuestionResult in the database (this part remains synchronous)
            q_results.append(QuestionResult(
                test=test,
                question=question,
                llm_response=content,
                answer=answer,
                explanation=explanation,
                correct=correct,
                response_time=0.5,
                confidence=confidence
            ))

        await sync_to_async(QuestionResult.objects.bulk_create)(q_results)

    except Exception as e:
        print(f"Error occurred during evaluation: {e}")


async def query_llm(llm_model, question, max_attempts=3, initial_delay=2):
    """
    Sends the question to the LLM model and retrieves the response with a retry mechanism.
    """

    prompt = (
        f"You are a cybersecurity expert. Analyze the following multiple-choice question and provide only the correct answer letter (A, B, C, or D).\n\n"
        f"Question:\n{question.question}\n\n"
        f"Options:\n"
        f"A: {question.option_a}\n"
        f"B: {question.option_b}\n"
        f"C: {question.option_c}\n"
        f"D: {question.option_d}\n\n"
        f"### Response Format:\n"
        f"Answer: <Correct answer letter (A, B, C, or D)>\n\n"
        f"### Example Response:\n"
        f"Answer: C"
    )

    attempt = 0
    delay = initial_delay  # Start with the initial delay time

    while attempt < max_attempts:
        try:
            response = await client.chat.completions.create(
                model=llm_model.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )

            if hasattr(response, "error"):
                error_code = response.error.get("code", "Unknown")
                error_message = response.error.get("message", "No message provided.")
                raise Exception(f"API Error {error_code}: {error_message}")

            content = response.choices[0].message.content.strip()


            if not content:
                print(f"Warning: Received empty response on attempt {attempt + 1}/{max_attempts}")
                attempt += 1
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                continue

            # Extract answer using regex
            answer_match = re.search(r"Answer:\s*([A-D])", content, re.IGNORECASE)
            answer = answer_match.group(1).strip().upper() if answer_match else "X"

            # Return answer if valid, else retry
            if answer in ["A", "B", "C", "D"]:
                print(f"Succes on attempt {attempt + 1}/{max_attempts}")
                return answer, "Not implemented yet", 0.0, content  # Only return answer and raw response

            print(f"Warning: Unexpected response format on attempt {attempt + 1}/{max_attempts}")
            attempt += 1
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff


        except Exception as e:
            error_msg = str(e)
            print(f"Error on attempt {attempt + 1}/{max_attempts}: {error_msg}")
            attempt += 1
            await asyncio.sleep(delay)
            delay *= 2  # Exponential backoff

    print("Failed to get a valid response after multiple retries.")
    return "X", "X", 0.0, "Error: No valid response received."





def compute_test_metrics(test):
    """
    Computes the test metrics.
    """
    results = QuestionResult.objects.filter(test=test)

    # Extract correct answers and predicted answers, filtering out 'X' (failed queries)
    y_true = [res.question.correct_option for res in results if res.answer != "X"]
    y_pred = [res.answer for res in results if res.answer != "X"]

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




    test.save()
