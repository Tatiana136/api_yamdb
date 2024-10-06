from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from reviews.models import User
from .serializers import TokenSerializer, SignupSerializer, AdminUserSerializer
from .permissions import IsAdmin


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(username__icontains=search_query)
        return queryset
    
    @action(methods=['GET', 'PATCH'], detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        """Изменение данных пользователя."""
        if request.method == 'GET':
            return Response(self.get_serializer(request.user).data, status=status.HTTP_200_OK)
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
    # Используется для ген-и случайных строк, который можно исп-ть как код подтв-я.
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
        # Проверяем, существует ли пользователь с таким email
        user = User.objects.get(username=username, email=email)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        try:
            user = User.objects.create(username=username, email=email)
            serializer = SignupSerializer(user, data=request.data, partial=True)
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
        return Response({"ERROR": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
    if not user.confirmation_code == confirmation_code:
        return Response({"ERROR": "Неверный код подтверждения."}, status=status.HTTP_400_BAD_REQUEST)
    user.is_active = True
    user.save()
    token = AccessToken.for_user(user)
    return Response({'token': str(token)}, status=status.HTTP_200_OK)
