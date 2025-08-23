from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
import csv
from .models import Blog,  CodeAnalysis, AnalysisIssue  # CORRECT - Remove BlogPost
from .services import CodeAnalyzerService  # Import the service

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

# Add these new views for code analysis

def analyzer_home(request):
    """Home page for code analyzer"""
    recent_analyses = CodeAnalysis.objects.all()[:10]
    
    # Get statistics
    total_analyses = CodeAnalysis.objects.count()
    completed_analyses = CodeAnalysis.objects.filter(status='completed').count()
    
    context = {
        'recent_analyses': recent_analyses,
        'total_analyses': total_analyses,
        'completed_analyses': completed_analyses,
    }
    return render(request, 'analyzer/home.html', context)

def analyze_code(request):
    """Handle code analysis requests"""
    if request.method == 'POST':
        code_content = request.POST.get('code_content', '').strip()
        language = request.POST.get('language')
        filename = request.POST.get('filename', 'untitled').strip() or 'untitled'
        
        if not code_content:
            messages.error(request, "Please provide code to analyze.")
            return redirect('analyzer_home')
        
        if len(code_content) > 50000:  # 50KB limit
            messages.error(request, "Code is too large. Please limit to 50KB.")
            return redirect('analyzer_home')
        
        # Create analysis record
        analysis = CodeAnalysis.objects.create(
            filename=filename,
            language=language,
            code_content=code_content,
            user_ip=request.META.get('REMOTE_ADDR'),
            status='pending'
        )
        
        try:
            # Run analysis
            analyzer = CodeAnalyzerService()
            results = analyzer.analyze_code(code_content, language, filename)
            
            # Save results
            analysis.analysis_result = results
            analysis.status = 'completed'
            analysis.save()
            
            # Create issue records
            all_issues = []
            all_issues.extend(results.get('security_issues', []))
            all_issues.extend(results.get('style_issues', []))
            all_issues.extend(results.get('ai_issues', []))
            
            for issue in all_issues:
                AnalysisIssue.objects.create(
                    analysis=analysis,
                    issue_type=issue.get('type', 'bug'),
                    severity=issue.get('severity', 'medium'),
                    title=issue.get('title', 'Unknown Issue'),
                    description=issue.get('description', ''),
                    line_number=issue.get('line_number'),
                    suggestion=issue.get('suggestion', '')
                )
            
            messages.success(request, f"Analysis completed! Found {len(all_issues)} issues.")
            return redirect('analysis_results', analysis_id=analysis.id)
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.analysis_result = {'error': str(e)}
            analysis.save()
            messages.error(request, f"Analysis failed: {str(e)}")
            return redirect('analyzer_home')
    
    return render(request, 'analyzer/analyze.html')

def analysis_results(request, analysis_id):
    """Display analysis results"""
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id)
    issues = analysis.issues.all().order_by('-severity', 'line_number')
    
    # Pagination
    paginator = Paginator(issues, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Group issues by type
    issues_by_type = {}
    for issue in issues:
        if issue.issue_type not in issues_by_type:
            issues_by_type[issue.issue_type] = []
        issues_by_type[issue.issue_type].append(issue)
    
    context = {
        'analysis': analysis,
        'issues': page_obj,
        'issues_by_type': issues_by_type,
        'total_issues': issues.count(),
    }
    return render(request, 'analyzer/results.html', context)

def download_report(request, analysis_id):
    """Download analysis report as CSV"""
    analysis = get_object_or_404(CodeAnalysis, id=analysis_id)
    issues = analysis.issues.all()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analysis_report_{analysis.id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Type', 'Severity', 'Title', 'Description', 'Line Number', 'Suggestion'])
    
    for issue in issues:
        writer.writerow([
            issue.issue_type,
            issue.severity,
            issue.title,
            issue.description,
            issue.line_number or '',
            issue.suggestion
        ])
    
    return response

@csrf_exempt
def api_analyze(request):
    """API endpoint for code analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code_content = data.get('code', '').strip()
            language = data.get('language', 'python')
            filename = data.get('filename', 'api_submission')
            
            if not code_content:
                return JsonResponse({'success': False, 'error': 'No code provided'})
            
            analyzer = CodeAnalyzerService()
            results = analyzer.analyze_code(code_content, language, filename)
            
            return JsonResponse({
                'success': True,
                'results': results
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
