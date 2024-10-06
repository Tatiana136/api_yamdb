from rest_framework import serializers
from django.contrib.auth import get_user_model

from reviews.models import (
    Category, Genre, Title,
    Comment, Review)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()

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
    
    category = CategoriesSerializer(many=False)
    genre = GenresSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при небезопасных запросах."""
    
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        required=True
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        required=True
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

    def create(self, validated_data):
        if Review.objects.filter(
            author=self.context['request'].user,
            title=validated_data.get('title')
        ).exists():
            raise serializers.ValidationError(
                'Нельзя оставить больше одного обзора.')

        review = Review.objects.create(**validated_data,)

        return review

    class Meta:
        model = Review
        exclude = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""
    
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        exclude = ('review',)
