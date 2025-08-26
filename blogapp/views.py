from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
import csv
from .models import Blog, CodeAnalysis, AnalysisIssue
from .services import CodeAnalyzerService

def home(request):
    # If user is already logged in, redirect to blog list
    if request.user.is_authenticated:
        return redirect('blog_list')
    return render(request, 'blog/home.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        # Create user in database
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=username.split()[0] if username else ''
            )
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, "Registration failed. Please try again.")
            return redirect('register')

    return render(request, 'blog/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome, {user.username}! You have successfully logged in!")
            return redirect('blog_list')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'blog/login.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('home')

def code_analysis(request):
    if request.method == 'POST':
        code_content = request.POST.get('code', '')
        language = request.POST.get('language', 'python')
        
        if not code_content.strip():
            messages.error(request, 'Please provide code content to analyze.')
            return render(request, 'blog/code_analysis.html')
        
        # Simple mock analysis for demonstration
        analysis_result = {
            'quality_score': 8.5,
            'issues': [
                {
                    'line': 5,
                    'message': 'Consider using more descriptive variable names',
                    'type': 'style',
                    'severity': 'low'
                },
                {
                    'line': 10,
                    'message': 'Missing error handling',
                    'type': 'logic',
                    'severity': 'medium'
                }
            ],
            'suggestions': [
                'Add proper error handling for edge cases',
                'Consider using type hints for better code documentation',
                'Add unit tests to ensure code reliability'
            ]
        }
        
        return render(request, 'blog/code_analysis.html', {'analysis_result': analysis_result})
    
    return render(request, 'blog/code_analysis.html')

@login_required
def collections(request):
    category = request.GET.get('category', 'all')
    
    # Updated category mapping
    category_mapping = {
        'food': 'food',
        'travel': 'travel', 
        'tech': 'Technology',
        'lifestyle': 'lifestyle',
        'education': 'education'
    }
    
    if category and category != 'all':
        # Map the category to the actual model field value
        actual_category = category_mapping.get(category, category)
        blogs = Blog.objects.filter(category__icontains=actual_category).order_by('-created_at')
    else:
        blogs = Blog.objects.all().order_by('-created_at')
    
    # Generate images for blogs that don't have them
    for blog in blogs:
        if not blog.image:
            from .utils import generate_blog_image
            generated_image = generate_blog_image(blog.title, blog.category, blog.author.username)
            if generated_image:
                blog.image = generated_image
                blog.save()
    
    return render(request, 'blog/collections.html', {'blogs': blogs})

def blog_detail(request, blog_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to view blog details.")
        return redirect('login')
    
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        messages.error(request, "The blog you are looking for does not exist.")
        return redirect('collections')

    return render(request, 'blog/blog_detail.html', {'blog': blog})

@login_required
def blog_list(request):
    category = request.GET.get('category')
    blogs = Blog.objects.all().order_by('-created_at')
    
    if category:
        blogs = blogs.filter(category=category)
    
    # Generate images for blogs that don't have them
    for blog in blogs:
        if not blog.image:
            from .utils import generate_blog_image
            generated_image = generate_blog_image(blog.title, blog.category, blog.author.username)
            if generated_image:
                blog.image = generated_image
                blog.save()
    
    # Pagination
    paginator = Paginator(blogs, 6)  # 6 blogs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blogs': page_obj,
        'categories': Blog.CATEGORY_CHOICES,
        'current_category': category,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    return render(request, 'blog/blog_list.html', context)

# Code Analyzer views remain the same
def analyzer_home(request):
    recent_analyses = CodeAnalysis.objects.all().order_by('-created_at')[:5]
    total_analyses = CodeAnalysis.objects.count()
    total_issues = AnalysisIssue.objects.count()
    
    context = {
        'recent_analyses': recent_analyses,
        'total_analyses': total_analyses,
        'total_issues': total_issues,
    }
    return render(request, 'analyzer/home.html', context)

def analyze_code(request):
    if request.method == 'POST':
        code_content = request.POST.get('code_content', '')
        filename = request.POST.get('filename', 'untitled.py')
        language = request.POST.get('language', 'python')
        
        if not code_content.strip():
            messages.error(request, 'Please provide code content to analyze.')
            return render(request, 'analyzer/analyze.html')
        
        # Create analysis record
        analysis = CodeAnalysis.objects.create(
            filename=filename,
            language=language,
            code_content=code_content,
            status='pending'
        )
        
        # Perform analysis
        try:
            analyzer = CodeAnalyzerService()
            results = analyzer.analyze_code(code_content, language, filename)
            
            # Save results
            for issue in results.get('issues', []):
                AnalysisIssue.objects.create(
                    analysis=analysis,
                    issue_type=issue.get('type', 'unknown'),
                    severity=issue.get('severity', 'info'),
                    line_number=issue.get('line', 0),
                    description=issue.get('description', ''),
                    suggestion=issue.get('suggestion', '')
                )
            
            analysis.status = 'completed'
            analysis.ai_feedback = results.get('ai_feedback', '')
            analysis.save()
            
            return redirect('analysis_results', analysis_id=analysis.id)
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.save()
            messages.error(request, f'Analysis failed: {str(e)}')
    
    return render(request, 'analyzer/analyze.html')

def analysis_results(request, analysis_id):
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id)
    issues = analysis.issues.all()
    
    context = {
        'analysis': analysis,
        'issues': issues,
    }
    return render(request, 'analyzer/results.html', context)

def download_report(request, analysis_id):
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id)
    issues = analysis.issues.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analysis_report_{analysis.id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Type', 'Severity', 'Line', 'Description', 'Suggestion'])
    
    for issue in issues:
        writer.writerow([
            issue.issue_type,
            issue.severity,
            issue.line_number,
            issue.description,
            issue.suggestion
        ])
    
    return response

@csrf_exempt
def api_analyze(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_content = data.get('code_content', '')
            language = data.get('language', 'python')
            filename = data.get('filename', 'untitled.py')
            
            if not code_content.strip():
                return JsonResponse({'error': 'No code content provided'}, status=400)
            
            analyzer = CodeAnalyzerService()
            results = analyzer.analyze_code(code_content, language, filename)
            
            return JsonResponse(results)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
