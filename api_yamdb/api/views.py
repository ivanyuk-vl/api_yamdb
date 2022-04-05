from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .pagination import CustomPagination
from .permissions import (AuthUserOrReadOnly, IsAdmin, IsAnonymous,
                          IsAuthenticated, IsAuthorOrReadOnly)
from .serializers import (CategoriesSerializer, CommentSerializer,
                          GenresSerializer, MeSerializer, ReviewSerializer,
                          SignUpSerializer, TokenSerializer,
                          TitlesSerializer, UserSerializer)
from reviews.models import Review, Titles, Categories, Genres
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

    permission_classes = (IsAnonymous,)

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        # TODO сделать отправку кода на почту !!!
        confirmation_code = generate_confirmation_code()
        print('*' * 30, confirmation_code, '*' * 30)
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
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    permission_classes = (AuthUserOrReadOnly,)
    pagination_class = CustomPagination
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Titles, id=self.kwargs.get('title_id'))

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
    permission_classes = (IsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(review=self.get_review(), author=self.request.user)
