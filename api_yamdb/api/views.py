from rest_framework import viewsets, status, mixins
from rest_framework import filters

from .pagination import CustomPagination
from .permissions import AuthUserOrReadOnly
from .serializers import TitlesSerializer, CategoriesSerializer, \
    GenresSerializer

from reviews.models import Titles, Categories, Genres


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination
    search_fields = ('name',)


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination
    search_fields = ('name',)
