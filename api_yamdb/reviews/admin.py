from django.contrib import admin

from .models import Categories, Comment, Genres, Review, Title


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


admin.site.register(Title, TitlesAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Genres, GenresAdmin)
admin.site.register(Review)
admin.site.register(Comment)
