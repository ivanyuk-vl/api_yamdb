from django.urls import path, include
from rest_framework import routers

from .views import TitlesViewSet, CategoriesViewSet, GenresViewSet

router = routers.DefaultRouter()
router.register('titles', TitlesViewSet)
router.register('categories', CategoriesViewSet)
router.register('genres', GenresViewSet)


urlpatterns = [
    path('v1/', include(router.urls)),
]