from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Расширение модели админа"""
    model = User
    list_display = ['email', 'username', 'confirmation_code',
                    'first_name', 'last_name',
                    'bio', 'role']
    list_editable = ['confirmation_code']


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    list_editable = ('name', 'year',)
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# Регистрируем расширенные модели пользователей и админа
admin.site.register(Review)
admin.site.register(Comment)
