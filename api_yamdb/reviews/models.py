from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

from api_yamdb.settings import (
    MAX_SCORE, MIN_SCORE, MIN_TITLE_YEAR
)
from users.models import User

CURRENT_YEAR = datetime.now().year
COMMENT_STR = 'id: {}, review_id: {}, Автор: {}, Дата публикации {}, Текст: {}'
REVIEW_STR = (
    'id: {}, Произведение: {}, Автор: {}, Дата публикации {}, '
    'Оценка: {}, Текст: {}'
)
YEAR_ERROR = 'Недопустимый год {}. Год должен быть в пределах {} < year <= {}.'


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True,
                            verbose_name='URL_Categories')

    class Meta:
        ordering = ('name',)
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True,
                            verbose_name='URL_Genres')

    class Meta:
        ordering = ('name',)
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


def validate_year(year):
    if not(MIN_TITLE_YEAR < year <= CURRENT_YEAR):
        raise ValidationError(YEAR_ERROR.format(
            year, MIN_TITLE_YEAR, CURRENT_YEAR
        ))


class Title(models.Model):
    name = models.TextField(
        verbose_name='Произведение',
        help_text='Введите название произведения'
    )
    year = models.IntegerField(
        default=CURRENT_YEAR,
        validators=[validate_year],
        verbose_name='Год создания произведения',
        help_text='Введите год создания произведения',
    )
    description = models.TextField(
        verbose_name='описание', help_text='Текст описания'
    )
    category = models.ForeignKey(
        Category,
        related_name='titles',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория',
        help_text='Выберите категорию'
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    class Meta:
        ordering = ('name',)
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='произведение'
    )
    text = models.TextField(verbose_name='текст', help_text='Текст отзыва')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='автор',
    )
    score = models.IntegerField(
        verbose_name='оценка',
        help_text='Оценка произведения',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации',
    )

    class Meta:
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            ),
            models.CheckConstraint(
                check=models.Q(score__range=(MIN_SCORE, MAX_SCORE)),
                name='score_range_1-10'
            ),
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return REVIEW_STR.format(
            self.pk,
            self.title.pk,
            self.author.username,
            self.pub_date.strftime('%d.%m.%Y %H:%M:%S'),
            self.score,
            self.text[:15],
        )


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )
    text = models.TextField(
        verbose_name='текст',
        help_text='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации',
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return COMMENT_STR.format(
            self.pk,
            self.review.pk,
            self.author.username,
            self.pub_date.strftime('%d.%m.%Y %H:%M:%S'),
            self.text[:15],
        )


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
