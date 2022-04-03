from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Расширенние модели админа"""
    model = CustomUser
    list_display = ['email', 'username', 'confirmation_code',
                    'first_name', 'last_name',
                    'bio', 'role']
    list_editable = ['confirmation_code']


# Регистрируем расширенные модели пользователей и админа
admin.site.register(CustomUser, CustomUserAdmin)
