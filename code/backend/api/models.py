from django.contrib.auth.models import User
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField


class BaseModel(models.Model):
    """Abstract base model for common fields."""
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserAPIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="api_key")
    api_key = EncryptedTextField()
    key_last4 = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ****{self.key_last4}"


class LLMModel(BaseModel):
    """"Large Language Model (LLM) representation"""
    model_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True, null=True)


    class Meta:
        verbose_name = "LLM Model"
        verbose_name_plural = "LLM Models"
        ordering = ['-created_at']   # Sort by created_at in descending order

    def __str__(self):
        return f"{self.name} by {self.provider})"


class Dataset(BaseModel):
    """Represents a dataset for testing LLMs."""
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=1000, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets', null=True)
    is_public = models.BooleanField(default=False)

    origin = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clones",
        db_index=True,
    )

    def get_total_questions(self):
        return self.questions.count()  # Counts related questions

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

    correct_answers = models.IntegerField(default=0)
    accuracy_percentage = models.FloatField(default=0.0)
    confidence_interval_low = models.FloatField(default=0.0)
    confidence_interval_high = models.FloatField(default=0.0)

    # Macro evaluation metrics
    precision_avg = models.FloatField(default=0.0)
    recall_avg = models.FloatField(default=0.0)
    f1_avg = models.FloatField(default=0.0)

    # Stores precision, recall, F1-score per answer choice
    class_metrics = models.JSONField(default=dict)

    # JSON storage for answer distribution
    answer_distribution = models.JSONField(default=dict)



    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Tests"
        ordering = ['-started_at']

    def __str__(self):
        return f"Test {self.id} by {self.user.username}"


class QuestionResult(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='results')
    llm_response = models.TextField()
    answer = models.CharField(max_length=1)
    correct = models.BooleanField()
    response_time = models.FloatField()

    class Meta:
        verbose_name = "Test Result"
        verbose_name_plural = "Test Results"
        ordering = ['test', 'question']

    def __str__(self):
        return f"Result for Question {self.question.id} in Test {self.test.id}"
