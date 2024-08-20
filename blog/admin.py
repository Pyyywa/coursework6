from django.contrib import admin

from blog.models import Article


@admin.register(Article)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_create', 'is_published',)
    list_filter = ('is_published',)
    search_fields = ('title',)
