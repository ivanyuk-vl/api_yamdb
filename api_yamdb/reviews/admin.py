from django.contrib import admin

from .models import Titles, Categories, Genres


class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'categories')
    list_editable = ('name', 'year',)
    search_fields = ('name',)
    list_filter = ('categories',)


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug',)
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class GenresAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_editable = ('name',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Titles, TitlesAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Genres, GenresAdmin)
