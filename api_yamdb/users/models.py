from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

ROLES = (
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CustomUser(AbstractUser):
    """Расширенние модели пользователя"""
    role = models.CharField(max_length=255, default='user')
    bio = models.CharField(max_length=255, blank=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


User = get_user_model()
