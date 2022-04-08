from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title
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
        return self.initial_data


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
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
        read_only_fields = [field.name for field in model._meta.fields]

    def get_rating(self, title):
        return getattr(title, 'rating', None)


class TitleSerializer(TitleGetSerializer):
    genre = SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title


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
