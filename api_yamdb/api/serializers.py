from rest_framework import serializers
from reviews.models import User
from api.validators import validate_username
from rest_framework.exceptions import ValidationError
import re

USERNAME_REGEX = r'^[\w.@+-]+\Z'


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'role',)


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True,
                                     validators=[validate_username])
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, value):
        """Проверка username на соответствие паттерну."""
        if value and not re.match(USERNAME_REGEX, value):
            raise ValidationError('Введите корректный username')
        return value


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        extra_kwargs = {'username': {'required': True}}

    def validate_username(self, value):
        """Проверка username на соответствие паттерну."""
        if value and not re.match(USERNAME_REGEX, value):
            raise ValidationError('Введите корректный username')
        return value

    def update(self, instance, validated_data):
        if 'role' in validated_data:
            validated_data.pop('role')
        # Вызываем метод update р.к. и передаем аргументы,
        # это позволит р.к. обрабатывать обновления экз-я
        # с уже проверенными данными.
        return super().update(instance, validated_data)
