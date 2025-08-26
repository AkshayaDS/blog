import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from django.conf import settings
from django.core.files.base import ContentFile
import hashlib
import textwrap

def generate_blog_image(title, category, author_name):
    """Generate a blog image based on title, category, and author"""
    try:
        # Create image dimensions
        width, height = 800, 400
        
        # Category color mapping for brown theme
        category_colors = {
            'Technology': '#8B4513',
            'Programming': '#A0522D', 
            'Tutorial': '#CD853F',
            'Review': '#DEB887',
            'News': '#D2691E',
            'Other': '#BC8F8F',
            'food': '#A0522D',
            'travel': '#8B4513',
            'tech': '#654321',
            'lifestyle': '#CD853F',
            'education': '#D2691E'
        }
        
        # Create image
        img = Image.new('RGB', (width, height), color='#F5F5DC')  # Beige background
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            subtitle_font = ImageFont.truetype("arial.ttf", 18)
            category_font = ImageFont.truetype("arial.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default() 
            category_font = ImageFont.load_default()
        
        # Get category color
        bg_color = category_colors.get(category, '#8B4513')
        
        # Draw category background
        draw.rectangle([0, 0, width, 80], fill=bg_color)
        
        # Draw category text
        draw.text((20, 25), f"Category: {category.title()}", fill='white', font=category_font)
        
        # Wrap title text
        wrapped_title = textwrap.fill(title, width=35)
        title_lines = wrapped_title.split('\n')
        
        # Draw title
        y_offset = 120
        for line in title_lines:
            draw.text((20, y_offset), line, fill='#2F1B14', font=title_font)
            y_offset += 40
        
        # Draw author
        draw.text((20, height - 60), f"By: {author_name}", fill='#654321', font=subtitle_font)
        
        # Draw decorative elements
        draw.rectangle([width-10, 0, width, height], fill=bg_color)
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG', quality=85)
        img_io.seek(0)
        
        # Create filename
        filename = f"blog_{hashlib.md5(title.encode()).hexdigest()[:8]}.jpg"
        
        return ContentFile(img_io.getvalue(), name=filename)
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def get_placeholder_image(category):
    """Get a placeholder image for the category"""
    try:
        # Use a placeholder service
        url = f"https://picsum.photos/800/400?random={category}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            filename = f"placeholder_{category.lower()}.jpg"
            return ContentFile(response.content, name=filename)
    except:
        pass
    return None
