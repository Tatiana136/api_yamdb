from rest_framework import mixins, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

<<<<<<< HEAD
from .permissions import (IsAdminPermission,
                          IsReadOnlyPermission)
=======
from .permissions import (ReadOnly, IsSuperUserOrIsAdmin)
>>>>>>> 36719b18e1d7a4208382dbf22ace15fd34cdf4ff


class CategoryGenreViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):

<<<<<<< HEAD
    permission_classes = [IsReadOnlyPermission | IsAdminPermission]
=======
    permission_classes = [ReadOnly | IsSuperUserOrIsAdmin]
>>>>>>> 36719b18e1d7a4208382dbf22ace15fd34cdf4ff
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
<<<<<<< HEAD


class TitleReviewCommentViewSet(viewsets.ModelViewSet):
    pass
=======
>>>>>>> 36719b18e1d7a4208382dbf22ace15fd34cdf4ff
