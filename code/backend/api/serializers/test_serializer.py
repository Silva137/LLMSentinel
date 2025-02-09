from rest_framework import serializers
from ..models import Test, Dataset, LLMModel
from ..serializers.dataset_serializer import DatasetSerializer
from ..serializers.llm_serializer import LLMModelSerializer
from ..serializers.question_serializer import QuestionResultSerializer
from ..serializers.user_serializer import UserSerializer


class TestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    dataset = DatasetSerializer(read_only=True)
    llm_model = LLMModelSerializer(read_only=True)
    results = QuestionResultSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class TestCreationSerializer(serializers.ModelSerializer):
    dataset_id = serializers.IntegerField(write_only=True, required=True)
    llm_model_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Test
        fields = ["id", "dataset_id", "llm_model_name"]

    def validate(self, attrs):

        dataset_id = attrs.get("dataset_id")
        llm_model_name = attrs.get("llm_model_name")

        if not Dataset.objects.filter(id=dataset_id).exists():
            raise serializers.ValidationError({"dataset_id": "Dataset not found."})

        if not LLMModel.objects.filter(name=llm_model_name).exists():
            raise serializers.ValidationError({"llm_model_name": "LLM Model not found."})

        return attrs

    def create(self, validated_data):

        dataset_id = validated_data.get("dataset_id")
        llm_model_name = validated_data.get("llm_model_name")

        dataset = Dataset.objects.get(id=dataset_id)
        llm_model = LLMModel.objects.filter(name=llm_model_name).first() # remove .first() and use get after fixing error of returning multiple llm models with same name
        request = self.context.get("request")

        return Test.objects.create(
            user=request.user,
            dataset=dataset,
            llm_model=llm_model
        )
