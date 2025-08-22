from django.contrib import admin
from django.utils.html import format_html
from .models import Blog, Comment, Favorite


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at', 'image_tag')
    list_filter = ('author', 'category', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="60" />'.format(obj.image.url))
        return "No Image"
    image_tag.short_description = 'Image'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'content', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'blog__title')
    ordering = ('-created_at',)


@admin.register(Favorite) 
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'added_at')
    list_filter = ('added_at', 'user')
    search_fields = ('user__username', 'blog__title')
    ordering = ('-added_at',)
