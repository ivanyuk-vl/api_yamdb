from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models

ROLES = (
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CustomUser(AbstractUser):
    """Расширенние модели пользователя"""
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, default='user')
    bio = models.CharField(max_length=255, blank=True)
    confirmation_code = models.CharField(max_length=255, blank=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


AnonymousUser.role = None
User = get_user_model()
