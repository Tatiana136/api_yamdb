from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import signup, get_token

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet
)


v1 = DefaultRouter()

v1.register('users', UserViewSet, basename='users')
v1.register('categories', CategoryViewSet, basename='categories')
v1.register('genres', GenreViewSet, basename='genres')
v1.register('titles', TitleViewSet, basename='titles')
v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

urlpatterns = [
    path('v1/auth/signup/', signup, name='signup'),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/', include(v1.urls)),
]
