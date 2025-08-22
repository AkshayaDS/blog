from django.shortcuts import render
from .models import Blog

def home(request):
    return render(request, 'blog/index.html')  # Root page with slider content

def register(request):
    return render(request, 'blog/register.html')  # Register page

def collections(request):
    blogs = Blog.objects.all()  # Fetch all blogs
    return render(request, 'blog/collections.html', {'blogs': blogs})  # Collections page
