from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home', views.home, name='home'),
    path('register', views.register, name='register'),
    path('collections/', views.collections, name="collections"),
] 