from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .permissions import (
    IsAdminOrReadOnly, IsAdminOrIsModeratorOrIsAuthorOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer,
    ReviewSerializer, SignUpSerializer, TitlesSerializer, UserSerializer
)
from reviews.models import Review, Title, Category, Genre
from users.models import User
from users.utils import generate_confirmation_code, get_tokens_for_user

UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение "{}"'
NOT_FOUND_PARAMS = 'Не найден один или несколько параметров: "{}".'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save(confirmation_code=generate_confirmation_code())

    @action(methods=['get', 'patch'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        instance = get_object_or_404(User, pk=request.user.id)

        if request.method == 'GET':
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['post'], detail=False)
    def signup(self, request):
        # TODO сделать отправку кода на почту !!!
        confirmation_code = generate_confirmation_code()
        print('*' * 30, confirmation_code, '*' * 30)
        request.data['confirmation_code'] = confirmation_code

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def token(self, request):
        if (not request.data['username']
                or not request.data['confirmation_code']):
            return Response({NOT_FOUND_PARAMS.format('"email" or "username"')},
                            status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, username=request.data['username'])
        if not request.data['confirmation_code'] == user.confirmation_code:
            return Response({'detail': 'Неверный код подтверждения'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = str(get_tokens_for_user(user))
        return Response({'token': token}, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrIsModeratorOrIsAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        if self.request.user.reviews.filter(title=title):
            raise ValidationError({'detail': UNIQUE_REVIEW_ERROR.format(
                self.request.user, title.name
            )})
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrIsModeratorOrIsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)
