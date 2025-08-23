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

@admin.register(CodeAnalysis)
class CodeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('filename', 'language', 'status', 'total_issues_display', 'created_at', 'user_ip')
    list_filter = ('language', 'status', 'created_at')
    search_fields = ('filename', 'user_ip')
    readonly_fields = ('analysis_result', 'created_at')
    ordering = ('-created_at',)
    
    def total_issues_display(self, obj):
        count = obj.total_issues
        if count == 0:
            return format_html('<span style="color: green;">✓ 0</span>')
        elif count < 5:
            return format_html('<span style="color: orange;">⚠ {}</span>', count)
        else:
            return format_html('<span style="color: red;">❌ {}</span>', count)
    total_issues_display.short_description = 'Issues Found'

@admin.register(AnalysisIssue)
class AnalysisIssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'analysis', 'issue_type', 'severity', 'line_number')
    list_filter = ('issue_type', 'severity', 'analysis__language')
    search_fields = ('title', 'description', 'analysis__filename')
    ordering = ('-analysis__created_at', 'line_number')