from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Расширенние модели админа"""
    model = CustomUser
    list_display = ['email', 'username']


# Регистрируем расширенные модели пользователей и админа
admin.site.register(CustomUser, CustomUserAdmin)
