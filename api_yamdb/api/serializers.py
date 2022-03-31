from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review, Title
from users.models import ROLES, User

SCORE_ERROR = 'Оценка должна быть в пределах от 1 до 10 включительно'


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=ROLES)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name',
                  'bio', 'role')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

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
        if score not in range(1, 11):
            raise serializers.ValidationError(SCORE_ERROR)
        return score


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Comment
        exclude = ('review',)
        read_only_fields = ('pub_date',)
