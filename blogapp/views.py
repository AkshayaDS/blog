from django.shortcuts import render
from . models import *

def home(request):
   
    return render(request, 'blog/index.html')

def register(request):
    
    return render(request, 'blog/register.html')

def collections(request):
    categories = Blog.CATEGORY_CHOICES   # Get all categories
    return render(request, 'blog/collections.html', {'categories': categories})


def collection(request):
    blogs = Blog.objects.all()

    category_defaults = {
        "food": "images/defaults/food.webp",
        "travel": "images/defaults/travel.jpg",
        "tech": "images/defaults/TECHNOLOGY.jpg",
        "lifestyle": "images/defaults/lifestyle.webp",
        "education": "images/defaults/edu.jpg",
    }

    return render(request, "collection.html", {
        "blogs": blogs,
        "category_defaults": category_defaults
    })
