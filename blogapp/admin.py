from django.contrib import admin
from django.utils.html import format_html
from .models import Blog, Comment, Favorite, CodeAnalysis, AnalysisIssue  # CORRECT

# Register your models here.
# Note: Only import and register models that actually exist in models.py

# If you have a BlogPost model, uncomment this:
# from .models import BlogPost
# admin.site.register(BlogPost)

# The CodeAnalysis and AnalysisIssue models will be added later
# after we create them in models.py

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'image_preview', 'created_at']
    list_filter = ['category', 'created_at', 'author']
    search_fields = ['title', 'content']
    ordering = ['-created_at']
    list_per_page = 20
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['blog', 'user', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']

@admin.register(CodeAnalysis)
class CodeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['filename', 'language', 'status', 'created_at']
    list_filter = ['language', 'status', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['filename', 'language']
    ordering = ['-created_at']

@admin.register(AnalysisIssue)
class AnalysisIssueAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'issue_type', 'severity', 'line_number']
    list_filter = ['issue_type', 'severity']
    search_fields = ['issue_type', 'description']
    ordering = ['analysis', 'line_number']