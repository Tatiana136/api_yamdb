from rest_framework import serializers
from reviews.models import User
from api.validators import validate_username
from rest_framework.exceptions import ValidationError
import re
from reviews.models import (
    Category,
    Genre,
    Title,
    Comment,
    Review
)

USERNAME_REGEX = r'^[\w.@+-]+\Z'


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


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


class CategoriesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenresSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    category = CategoriesSerializer(read_only=True)
    genre = GenresSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при небезопасных запросах."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
    )

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, title):
        serializer = TitleGETSerializer(title)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Нельзя оставлять более одного отзыва на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        exclude = ('review',)
