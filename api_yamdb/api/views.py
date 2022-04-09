from django.core.mail import send_mail
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast, Round
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
from users.utils import get_tokens_for_user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username',)
    ordering = ['id']

    def perform_create(self, serializer):
        serializer.save(confirmation_code=User.objects.make_random_password())

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        instance = get_object_or_404(User, pk=request.user.id)
        self.serializer_class = MeSerializer
        serializer = self.get_serializer(instance=instance)
        if request.method == 'PATCH':
            serializer.partial = True
            serializer.initial_data = request.data
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        confirmation_code = User.objects.make_random_password()
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                defaults={'confirmation_code': confirmation_code}
            )
        except Exception as ex:
            return Response({'detail': f'Внутренняя ошибка сервера \'{ex}\''},
                            status=status.HTTP_400_BAD_REQUEST)
        send_mail(
            'confirmation code',
            f'"confirmation_code":  {confirmation_code}',
            None,  # DEFAULT_FROM_EMAIL добавлен в settings
            [serializer.validated_data["email"]]
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def token(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'])
        if (not serializer.validated_data['confirmation_code']
                == user.confirmation_code):
            raise ValidationError({'detail': 'Неверный код подтверждения.'})

        serializer.validated_data['token'] = get_tokens_for_user(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Cast(
        Round(Avg('reviews__score')), IntegerField()
    )).order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer


class CategoryGenreBase(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CategoryGenreBase):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreBase):
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
        serializer.save(title=self.get_title(), author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrIsModeratorOrIsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)
