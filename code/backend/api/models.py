import uuid
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models


class BaseModel(models.Model):
    """Abstract base model for common fields."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LLMModel(BaseModel):
    """"Large Language Model (LLM) representation"""
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    api_url = models.URLField(validators=[URLValidator(schemes=['https'])])

    class Meta:
        verbose_name = "LLM Model"
        verbose_name_plural = "LLM Models"
        ordering = ['-created_at']   # Sort by created_at in descending order

    def __str__(self):
        return f"{self.name} (v{self.model})"


class Dataset(BaseModel):
    """Represents a dataset for testing LLMs."""
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = "Dataset"
        verbose_name_plural = "Datasets"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Question(BaseModel):
    """Represents a single multiple-choice question from certain dataset."""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField(max_length=2000)
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    difficulty = models.CharField(max_length=6, choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')])
    domain = models.CharField(max_length=500)
    explanation = models.TextField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['dataset', 'created_at']

    def __str__(self):
        return self.question[:50]


class Test(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tests')
    llm_model = models.ForeignKey(LLMModel, on_delete=models.CASCADE, related_name='tests')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='tests')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"
        ordering = ['-started_at']

    def __str__(self):
        return f"Test {self.id} by {self.user.username}"


class TestResult(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='results')
    llm_response = models.TextField()
    correct = models.BooleanField()
    response_time = models.FloatField()

    class Meta:
        verbose_name = "Test Result"
        verbose_name_plural = "Test Results"
        ordering = ['test', 'question']

    def __str__(self):
        return f"Result for Question {self.question.id} in Test {self.test.id}"
