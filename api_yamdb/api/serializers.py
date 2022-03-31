from rest_framework import serializers

from reviews.models import Titles, Categories, Genres


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
