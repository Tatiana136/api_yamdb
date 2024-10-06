from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from reviews.models import Category, Genre, Title, Review
from .filters import TitlesFilter
from .mixin import CategoryGenreViewSet, TitleReviewCommentViewSet
from .permissions import (IsAuthorPermission,
                          IsAdminPermission,
                          IsReadOnlyPermission)

from .serializers import (CategoriesSerializer,
                          GenresSerializer,
                          TitleSerializer,
                          TitleGETSerializer,
                          CommentSerializer,
                          ReviewSerializer,
                          UserSerializer
                          )


class UserViewSet(ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminPermission)
    lookup_field = 'username'
    search_fields = ('username',)


class CategoryViewSet(CategoryGenreViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenreViewSet(CategoryGenreViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitleViewSet(TitleReviewCommentViewSet):
    """Вьюсет для модели Title."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = [IsReadOnlyPermission | IsAdminPermission]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(TitleReviewCommentViewSet):
    """Вьюсет для модели Review."""

    permission_classes = IsAuthorPermission,
    pagination_class = PageNumberPagination
    serializer_class = ReviewSerializer

    def get_title(self):
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, id=title_id)


    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(TitleReviewCommentViewSet):
    """Вьюсет для модели Comment."""

    permission_classes = IsAuthorPermission,
    pagination_class = PageNumberPagination
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_review())
