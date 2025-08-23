from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Blog

def home(request):
    return render(request, 'blog/index.html')  # Root page with slider content

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password == confirm_password:
            # Store user data in session (replace with database logic in production)
            if 'users' not in request.session:
                request.session['users'] = []
            request.session['users'].append({'username': username, 'email': email, 'password': password})
            request.session.modified = True
            messages.success(request, "You have successfully registered!")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

    return render(request, 'blog/register.html')  # Render the register page

def collections(request):
    if not request.session.get('logged_in'):
        messages.error(request, "You need to log in to view collections.")
        return redirect('login')

    blogs = Blog.objects.all()  # Fetch all blogs
    return render(request, 'blog/collections.html', {'blogs': blogs})  # Render the collections page

def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate credentials against registered users
        users = request.session.get('users', [])
        for user in users:
            if user['email'] == email and user['password'] == password:
                request.session['logged_in'] = True
                request.session['username'] = user['username']
                messages.success(request, f"Welcome, {user['username']}! You have successfully logged in!")
                return redirect('collections')

        messages.error(request, "Invalid email or password.")
        return redirect('login')

    return render(request, 'blog/login.html')  # Render the login page

def logout(request):
    request.session.flush()  # Clear the session
    messages.success(request, "You have successfully logged out!")
    return redirect('home')  # Redirect to the home page after logout

def blog_detail(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)  # Fetch the blog by its ID
    except Blog.DoesNotExist:
        messages.error(request, "The blog you are looking for does not exist.")
        return redirect('collections')  # Redirect to collections if blog not found

    return render(request, 'blog/blog_detail.html', {'blog': blog})  # Render the blog detail page
