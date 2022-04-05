from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import TitleFilter
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAdminOrIsModeratorOrIsAuthorOrReadOnly
)
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, MeSerializer,
    ReviewSerializer, SignUpSerializer, TitleGetSerializer, TitleSerializer,
    TokenSerializer, UserSerializer
)
from reviews.models import Review, Title, Category, Genre
from users.models import User
from users.utils import generate_confirmation_code, get_tokens_for_user

UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение "{}"'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username',)
    ordering = ['username']

    def perform_create(self, serializer):
        serializer.save(confirmation_code=generate_confirmation_code())

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        instance = get_object_or_404(User, pk=request.user.id)
        serializer = MeSerializer(instance=instance)
        if request.method == 'PATCH':
            serializer.initial_data = request.data
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        confirmation_code = generate_confirmation_code()
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(confirmation_code=confirmation_code)
        user = serializer.instance
        send_mail(
            'confirmation code',
            f'"confirmation_code": "{user.confirmation_code}"',
            None,
            [user.email]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'])
        serializer.validated_data['token'] = get_tokens_for_user(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class CategoryViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin,
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(CategoryViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


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
