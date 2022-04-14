from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import (
    max_score_validator, min_score_validator,
    UsernameValidator, UsernameMeValidator, year_validator
)

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)
COMMENT_STR = 'id: {}, review_id: {}, Автор: {}, Дата публикации {}, Текст: {}'
REVIEW_STR = (
    'id: {}, Произведение: {}, Автор: {}, Дата публикации {}, '
    'Оценка: {}, Текст: {}'
)


class CustomUser(AbstractUser):
    """Расширение модели пользователя"""
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[UsernameValidator(), UsernameMeValidator()],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.'},
    )
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.TextField(default=USER, choices=ROLES)
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(max_length=255, blank=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR


User = get_user_model()


class CategoryAndGenreBase(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(CategoryAndGenreBase):

    class Meta(CategoryAndGenreBase.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'категории'


class Genre(CategoryAndGenreBase):

    class Meta(CategoryAndGenreBase.Meta):
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'


class Title(models.Model):
    name = models.TextField(
        verbose_name='Произведение',
        help_text='Введите название произведения'
    )
    year = models.IntegerField(
        default=datetime.now().year,
        validators=[year_validator],
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


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class CommentAndReviewBase(models.Model):
    text = models.TextField(verbose_name='текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации',
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class Review(CommentAndReviewBase):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='произведение'
    )
    score = models.IntegerField(
        validators=[min_score_validator, max_score_validator],
        verbose_name='оценка',
        help_text='Оценка произведения',
    )

    class Meta(CommentAndReviewBase.Meta):
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
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


class Comment(CommentAndReviewBase):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв',
    )

    class Meta(CommentAndReviewBase.Meta):
        default_related_name = 'comments'
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
