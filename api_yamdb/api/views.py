from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from reviews.models import Category, Genre, Title, Review, User
from api.serializers import (
    TokenSerializer,
    SignupSerializer,
    AdminUserSerializer,
    CategoriesSerializer,
    GenresSerializer,
    TitleSerializer,
    TitleGETSerializer,
    CommentSerializer,
    ReviewSerializer,
)
from api.permissions import (
    IsAdmin,
    ReadOnly,
    IsSuperUserIsAdminIsModeratorIsAuthor,
    IsSuperUserOrIsAdmin
)
from api.mixin import CategoryGenreViewSet
from api.filters import TitlesFilter


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Фильтрация на основе search."""
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        return queryset

    @action(methods=['GET', 'PATCH'], detail=False,
            url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """Изменение данных пользователя."""
        if request.method == 'GET':
            return Response(
                self.get_serializer(request.user).data,
                status=status.HTTP_200_OK
            )
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def send_confirmation_email(user):
    # default_token_generator - генератор токенов.
    # Используется для ген-и случайных строк,
    # который можно исп-ть как код подтв-я.
    # make_token - результат, случайный токен.
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Код подтверждения'
    message = f'Код авторизации: {confirmation_code}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    return send_mail(subject, message, from_email, recipient_list)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """Регистрация нового пользователя."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    try:
        user = User.objects.get(username=username, email=email)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        try:
            user = User.objects.create(username=username, email=email)
            serializer = SignupSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            send_confirmation_email(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Получение JWT-токена."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"ERROR": "Пользователь не найден."},
                        status=status.HTTP_404_NOT_FOUND)
    if not user.confirmation_code == confirmation_code:
        return Response({"ERROR": "Неверный код подтверждения."},
                        status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.save()
    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)


class CategoryViewSet(CategoryGenreViewSet):
    """Вьюсет для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class GenreViewSet(CategoryGenreViewSet):
    """Вьюсет для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenresSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Title."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (ReadOnly | IsSuperUserOrIsAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsSuperUserIsAdminIsModeratorIsAuthor
    )
    pagination_class = PageNumberPagination
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'patch']

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""

    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsSuperUserIsAdminIsModeratorIsAuthor
    )
    pagination_class = PageNumberPagination
    serializer_class = CommentSerializer
    http_method_names = ['get', 'head', 'options', 'post', 'delete', 'patch']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
