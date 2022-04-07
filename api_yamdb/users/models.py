from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models


class UserRole:
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'


ROLES = (
    (UserRole.USER, 'Аутентифицированный пользователь'),
    (UserRole.MODERATOR, 'Модератор'),
    (UserRole.ADMIN, 'Администратор'),
)


class CustomUser(AbstractUser):
    """Расширенние модели пользователя"""
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=255, default=UserRole.USER)
    bio = models.CharField(max_length=255, blank=True)
    confirmation_code = models.CharField(max_length=255, blank=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR


AnonymousUser.role = None
AnonymousUser.is_admin = False

User = get_user_model()
