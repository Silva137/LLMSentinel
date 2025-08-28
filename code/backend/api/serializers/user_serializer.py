from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import UserAPIKey


class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    # Custom logic for serializer.save()
    def create(self, validate_data):
        validate_data.pop('password2')
        user = User.objects.create_user(**validate_data)
        return user

        # Validating Password and Confirm Password while Registration

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Passwords do not match match")

        # Check if the email is already registered
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already registered.")

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserAPIKeySerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True)

    class Meta:
        model = UserAPIKey
        fields = ("api_key",)

    def create(self, validated_data):
        user = self.context.get("request").user
        api_key = validated_data["api_key"].strip()
        return UserAPIKey.objects.create(
            user=user,
            api_key=api_key,
            key_last4=api_key[-4:]
        )
