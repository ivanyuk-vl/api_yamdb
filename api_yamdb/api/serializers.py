from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Comment, Review, User

SCORE_ERROR = 'Оценка должна быть в пределах от 1 до 10 включительно'


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username', queryset=User.objects.all()
    )

    class Meta:
        fields = '__all__'
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
