import datetime

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

YEAR_CHOICES = []
for year in range(1700, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((year, year))


class Titles(models.Model):
    name = models.TextField(
        max_length=200,
        verbose_name='Произведение',
        help_text='Введите название произведения'
    )

    year = models.IntegerField(
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year,
        verbose_name='Год создания произведения',
        help_text='Введите год создания произведения',
    )

    categories = models.ForeignKey(
        'Categories',
        related_name='titles',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Выберите категорию'
    )

    genres = models.ManyToManyField(
        'Genres',
        related_name='titles',
        verbose_name='Жанр',
    )

    def __str__(self):
        return self.name


class Categories(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name="URL_Categories")

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name="URL_Genres")

    def __str__(self):
        return self.name

