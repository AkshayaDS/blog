from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('tech', 'Technology'),
        ('lifestyle', 'Lifestyle'),
        ('education', 'Education'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='lifestyle')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="favorites")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} favorited {self.blog}"


# Add these new models for code analysis
class CodeAnalysis(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('java', 'Java'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('cpp', 'C++'),
        ('c', 'C'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    filename = models.CharField(max_length=200, default='untitled')
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    code_content = models.TextField()
    analysis_result = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analysis of {self.filename} ({self.language})"
    
    @property
    def total_issues(self):
        if not self.analysis_result:
            return 0
        return len(self.analysis_result.get('security_issues', [])) + \
               len(self.analysis_result.get('style_issues', [])) + \
               len(self.analysis_result.get('ai_issues', []))

class AnalysisIssue(models.Model):
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    TYPE_CHOICES = [
        ('security', 'Security'),
        ('bug', 'Bug'),
        ('style', 'Style'),
        ('performance', 'Performance'),
        ('best_practice', 'Best Practice'),
    ]
    
    analysis = models.ForeignKey(CodeAnalysis, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    line_number = models.IntegerField(null=True, blank=True)
    suggestion = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.severity})"
