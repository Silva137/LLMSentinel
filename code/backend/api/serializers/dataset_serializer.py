import pandas as pd
from rest_framework import serializers

from .user_serializer import UserSerializer
from ..models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    total_questions = serializers.IntegerField(source='get_total_questions', read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Dataset
        fields = '__all__'


class DatasetUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    name = serializers.CharField(max_length=50, required=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):

        file = attrs.get("file")
        file_name = attrs.get("name")

        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("Invalid file type. Only CSV files are allowed.")

        try:
            dataset = pd.read_csv(file, sep=';', skiprows=1)

            # Verificar valores ausentes
            if dataset.isnull().any().any():
                raise serializers.ValidationError(f"O dataset '{file_name}' contém valores ausentes.")

            # Verificar se todas as colunas obrigatórias estão presentes
            required_columns = ["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"]

            for col in required_columns:
                if col not in dataset.columns.str.strip():
                    raise serializers.ValidationError(
                        f"O dataset '{file_name}' está com a seguinte coluna obrigatória ausente: {col}")

            # Verificar se 'Correct Answer' contém apenas valores válidos (A, B, C, D)
            if not dataset['Correct Answer'].str.strip().isin(['A', 'B', 'C', 'D']).all():
                raise serializers.ValidationError(
                    f"O dataset '{file_name}' contém valores inválidos na coluna 'Correct Answer'. Apenas 'A', 'B', 'C' ou 'D' são permitidos.")

        except Exception as e:
            raise serializers.ValidationError(f"Error reading CSV file: {e}")

        return file
