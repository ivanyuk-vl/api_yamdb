from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import UsernameMeValidator, UsernameValidator


SCORE_ERROR = 'Оценка должна быть в пределах от {} до {} включительно.'
UNIQUE_REVIEW_ERROR = 'У пользователя {} уже есть отзыв на произведение "{}".'
ME_USERNAME_ERROR = "Недопустимое имя пользователя 'me'"


class ValidateUsernameMixin:
    def validate_username(self, username):
        UsernameValidator()(username)
        UsernameMeValidator()(username)
        return username


class UserSerializer(serializers.ModelSerializer, ValidateUsernameMixin):

    class Meta:
        model = User
        fields = ('username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')
        required_fields = ('username', 'email')


class MeSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer, ValidateUsernameMixin):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = '__all__'


class SignUpSerializer(serializers.Serializer, ValidateUsernameMixin):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        fields = '__all__'


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
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )
        model = Title
        read_only_fields = fields


class TitleSerializer(TitleGetSerializer):
    genre = SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        exclude = ('title',)

    def validate(self, attrs):
        if self.context['request'].method != 'POST':
            return super().validate(attrs)
        title = get_object_or_404(
            Title,
            id=self.context['request'].parser_context['kwargs'].get('title_id')
        )
        author = self.context['request'].user
        if author and author.reviews.filter(title=title):
            raise ValidationError({'detail': UNIQUE_REVIEW_ERROR.format(
                author, title.name
            )})
        return super().validate(attrs)


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)
