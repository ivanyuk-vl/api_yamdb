from django.core.mail import send_mail
from django.db.models import Avg, IntegerField
from django.db.models.functions import Cast, Round
from django.db.utils import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
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
from reviews.models import Review, Title, Category, Genre, User
from reviews.utils import get_tokens_for_user

UNIQUE_ERROR = 'Пользователь с таким {} уже есть.'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('username',)
    ordering = ['username']

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = MeSerializer(instance=request.user)
        if request.method == 'PATCH':
            serializer.partial = True
            serializer.initial_data = request.data
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    confirmation_code = User.objects.make_random_password()
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user, _ = User.objects.update_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            defaults={'confirmation_code': confirmation_code}
        )
    except IntegrityError as ex:
        fail, field = ex.args and ex.args[0].split(': ')
        if fail != 'UNIQUE constraint failed':
            raise IntegrityError(ex)
        return Response(
            {'detail': UNIQUE_ERROR.format(field.split('.')[1])},
            status=status.HTTP_400_BAD_REQUEST
        )
    send_mail(
        'confirmation code',
        f'"confirmation_code": "{confirmation_code}"',
        None,  # DEFAULT_FROM_EMAIL добавлен в settings
        [serializer.validated_data["email"]]
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username'])
    if (not serializer.validated_data['confirmation_code']
            == user.confirmation_code):
        raise ValidationError({'detail': 'Неверный код подтверждения.'})

    return Response({'token': str(get_tokens_for_user(user))})


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Cast(
        Round(Avg('reviews__score')), IntegerField()
    ))
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGetSerializer
        return TitleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            TitleGetSerializer(instance=instance).data,
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs)


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
