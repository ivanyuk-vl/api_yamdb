from django.contrib import admin

from .models import Category, Comment, Genre, Review, Title


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'categories')
    list_editable = ('name', 'year',)
    search_fields = ('name',)
    list_filter = ('categories',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Title, TitlesAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review)
admin.site.register(Comment)
