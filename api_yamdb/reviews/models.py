from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
REVIEW_STR = 'id: {}, Автор: {}, Дата публикации {}, Оценка: {}, Текст: {}'
COMMENT_STR = 'id: {}, review_id: {}, Автор: {}, Дата публикации {}, Текст: {}'


class Review(models.Model):
    text = models.TextField(
        verbose_name='текст',
        help_text='Текст отзыва'
    )
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
            models.CheckConstraint(
                check=models.Q(score__gte=1, score__lte=10),
                name='score_gte_1_&_lte_10'
            )
        ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'

    def __str__(self):
        return REVIEW_STR.format(
            self.pk,
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
