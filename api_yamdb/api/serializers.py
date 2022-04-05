from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField

from reviews.models import Categories, Comment, Genres, Review, Titles
from reviews.settings import MAX_SCORE, MIN_SCORE
from users.models import ROLES, User

SCORE_ERROR = 'Оценка должна быть в пределах от {} до {} включительно'


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES, default='user')

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')
        required_fields = ('username', 'email')


class MeSerializer(serializers.ModelSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('username', 'email', 'role')


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = User
        fields = ('token',)
        read_only_fields = ('username', 'confirmation_code')

    def validate(self, data):
        if 'username' not in self.initial_data:
            raise ValidationError({'username': 'Обязательное поле.'})
        if 'confirmation_code' not in self.initial_data:
            raise ValidationError({
                'confirmation_code': 'Обязательное поле.'})
        user = get_object_or_404(User, username=self.initial_data['username'])
        if (not self.initial_data['confirmation_code']
                == user.confirmation_code):
            raise ValidationError({'detail': 'Неверный код подтверждения.'})
        return self.initial_data


class SignUpSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'confirmation_code')

    def validate_username(self, username):
        if username == 'me':
            raise ValidationError("Недопустимое имя пользователя 'me'")
        return username


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Categories


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genres


class TitlesSerializer(serializers.ModelSerializer):
    genres = GenresSerializer(many=True, read_only=True)
    categories = CategoriesSerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'genres', 'categories')
        model = Titles

    def get_rating(self, title):
        return (
            (title.reviews.count() or None)
            and round(title.reviews.aggregate(Avg('score'))['score__avg'])
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        exclude = ('title',)
        read_only_fields = ('pub_date',)

    def validate_score(self, score):
        if score not in range(MIN_SCORE, MAX_SCORE + 1):
            raise serializers.ValidationError(SCORE_ERROR.format(
                MIN_SCORE, MAX_SCORE
            ))
        return score


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)
        read_only_fields = ('pub_date',)
