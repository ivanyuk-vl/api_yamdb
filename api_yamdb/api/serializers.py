from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review, Title, User

SCORE_ERROR = 'Оценка должна быть в пределах от 1 до 10 включительно'


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Title

    def get_rating(self, obj):
        return (
            (obj.reviews.count() or None)
            and round(obj.reviews.aggregate(Avg('score'))['score__avg'])
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    class Meta:
        exclude = ('title',)
        model = Review
        read_only_fields = ('pub_date',)

    def validate_score(self, score):
        if score not in range(1, 11):
            raise serializers.ValidationError(SCORE_ERROR)
        return score


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    class Meta:
        exclude = ('review',)
        model = Comment
        read_only_fields = ('pub_date',)
