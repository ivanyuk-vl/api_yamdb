from django.core.mail import send_mail
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
    ReviewSerializer, SignUpSerializer, TitlesSerializer,
    CodeSerializer, UserSerializer
)
from reviews.models import Review, Title, Category, Genre
from users.models import User
from users.utils import generate_confirmation_code, get_tokens_for_user

CODE_ERROR = 'Неверный код подтверждения.'
UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение "{}"'


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
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(**serializer.validated_data).count():
            user = User.objects.get(**serializer.validated_data)
        else:
            user_serializer = UserSerializer(data=serializer.validated_data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            user = user_serializer.instance
        user.confirmation_code = generate_confirmation_code()
        user.save()
        send_mail(
            'confirmation code',
            f'"confirmation_code": "{user.confirmation_code}"',
            None,
            [user.email]
        )
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def token(self, request):
        serializer = CodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if user.confirmation_code != serializer.validated_data[
            'confirmation_code'
        ]:
            raise ValidationError({'confirmation_code': CODE_ERROR})
        return Response({'token': str(get_tokens_for_user(user))})


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
