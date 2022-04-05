from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TitlesViewSet, CategoriesViewSet, GenresViewSet

app_name = 'api'

router = DefaultRouter()
router.register('titles', TitlesViewSet, basename='titles')
router.register('categories', CategoriesViewSet, basename='categories')
router.register('genres', GenresViewSet, basename='genres')


urlpatterns = [
    path('v1/', include(router.urls)),
]
