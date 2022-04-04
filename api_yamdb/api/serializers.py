from django.db.models import Avg
from django.forms import ValidationError
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title
from reviews.settings import MAX_SCORE, MIN_SCORE
from users.models import ROLES, User

SCORE_ERROR = 'Оценка должна быть в пределах от {} до {} включительно.'
USERNAME_ERROR = 'Недопустимое имя пользователя: "{}".'


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES, default='user')

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    def validate_username(self, username):
        name = 'me'
        if username == name:
            raise ValidationError(USERNAME_ERROR.format(name))
        return username


class CodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitlesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    categories = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

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
