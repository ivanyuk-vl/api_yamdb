from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Categories, Comment, Genres, Review, Title
from reviews.settings import MAX_SCORE, MIN_SCORE
from users.models import ROLES, User

SCORE_ERROR = 'Оценка должна быть в пределах от {} до {} включительно'


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES, default='user')

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')


class SignUpSerializer(serializers.ModelSerializer):
    confirmation_code = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'confirmation_code')


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
