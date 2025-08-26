"""
URL configuration for blog_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blogapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Simple home page
    path('blogs/', views.blog_list, name='blog_list'),  # Blog list (requires auth)
    path('register/', views.register, name='register'),  # Register page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),  # Logout page
    path('collections/', views.collections, name='collections'),  # Collections page
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),  # Blog detail page
    
    # Code Analyzer URLs
    path('code-analysis/', views.code_analysis, name='code_analysis'),
    path('analyzer/', views.analyzer_home, name='analyzer_home'),
    path('analyzer/analyze/', views.analyze_code, name='analyze_code'),
    path('analyzer/results/<int:analysis_id>/', views.analysis_results, name='analysis_results'),
    path('analyzer/download/<int:analysis_id>/', views.download_report, name='download_report'),
    path('analyzer/api/analyze/', views.api_analyze, name='api_analyze'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
