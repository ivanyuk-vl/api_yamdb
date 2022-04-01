from django.contrib.auth import get_user_model
from django.db import models

from .settings import MAX_SCORE, MIN_SCORE

User = get_user_model()
REVIEW_STR = (
    'id: {}, Произведение: {}, Автор: {}, Дата публикации {}, '
    'Оценка: {}, Текст: {}'
)
COMMENT_STR = 'id: {}, review_id: {}, Автор: {}, Дата публикации {}, Текст: {}'


class Title(models.Model):
    name = models.TextField(
        verbose_name='название', help_text='Название произведения'
    )


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
