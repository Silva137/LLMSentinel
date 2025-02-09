from rest_framework import serializers
from ..models import LLMModel


class LLMModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMModel
        fields = '__all__'
