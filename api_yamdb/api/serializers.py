from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, GenreTitle, Title
from api_yamdb.settings import MAX_SCORE, MIN_SCORE
from users.models import ROLES, User

SCORE_ERROR = 'Оценка должна быть в пределах от {} до {} включительно.'
UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение "{}".'


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


class TokenSerializer(serializers.Serializer):
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


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, title):
        return (
            (title.reviews.count() or None)
            and round(title.reviews.aggregate(Avg('score'))['score__avg'])
        )


class TitleSerializer(TitleGetSerializer):
    genre = SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenreTitle.objects.create(title=title, genre=genre)
        return title


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

    def save(self, **kwargs):
        author = kwargs.get('author')
        title = kwargs.get('title')
        if author and author.reviews.filter(title=title):
            raise ValidationError({'detail': UNIQUE_REVIEW_ERROR.format(
                author, title
            )})
        return super().save(**kwargs)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)
        read_only_fields = ('pub_date',)
