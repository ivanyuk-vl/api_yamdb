from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentSerializer, ReviewSerializer, TitleSerializer, UserSerializer
)
from reviews.models import Review, Title
from users.models import User

UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение {}'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    @action(methods=['get', 'patch'], detail=False)
    def me(self, request):
        instance = get_object_or_404(User, pk=request.user)

        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        if self.request.user.reviews.filter(title=title):
            raise ValidationError(UNIQUE_REVIEW_ERROR.format(
                self.request.user, title.name
            ))
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)
