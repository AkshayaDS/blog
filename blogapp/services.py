import subprocess
import tempfile
import os
import json
import re
from django.conf import settings
import openai

class CodeAnalyzerService:
    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def analyze_code(self, code_content, language, filename):
        """Main method to analyze code using multiple tools"""
        results = {
            'security_issues': [],
            'style_issues': [],
            'ai_issues': [],
            'summary': {
                'total_lines': len(code_content.split('\n')),
                'language': language,
                'filename': filename
            }
        }
        
        try:
            # Run static analysis based on language
            if language == 'python':
                results['security_issues'] = self._run_bandit(code_content)
                results['style_issues'] = self._run_flake8(code_content)
            elif language == 'javascript':
                results['style_issues'] = self._basic_js_analysis(code_content)
            
            # Run AI analysis if API key is available
            if self.openai_api_key:
                results['ai_issues'] = self._ai_code_review(code_content, language)
            
            # Generate summary
            results['summary']['security_count'] = len(results['security_issues'])
            results['summary']['style_count'] = len(results['style_issues'])
            results['summary']['ai_count'] = len(results['ai_issues'])
            results['summary']['total_issues'] = (
                results['summary']['security_count'] + 
                results['summary']['style_count'] + 
                results['summary']['ai_count']
            )
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _run_bandit(self, code_content):
        """Run Bandit security scanner for Python code"""
        security_issues = []
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name
            
            result = subprocess.run(
                ['bandit', '-f', 'json', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_file_path)
            
            if result.stdout:
                bandit_output = json.loads(result.stdout)
                for issue in bandit_output.get('results', []):
                    security_issues.append({
                        'title': issue.get('test_name', 'Security Issue'),
                        'description': issue.get('issue_text', ''),
                        'severity': issue.get('issue_severity', 'medium').lower(),
                        'line_number': issue.get('line_number'),
                        'confidence': issue.get('issue_confidence', 'medium'),
                        'type': 'security'
                    })
        except Exception as e:
            security_issues.append({
                'title': 'Bandit Analysis Error',
                'description': f'Could not run security analysis: {str(e)}',
                'severity': 'info',
                'type': 'security'
            })
        
        return security_issues
    
    def _run_flake8(self, code_content):
        """Run Flake8 style checker for Python code"""
        style_issues = []
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name
            
            result = subprocess.run(
                ['flake8', '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_file_path)
            
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Parse flake8 output
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        style_issues.append({
                            'title': f'Style Issue: {parts[3].split()[0] if parts[3].split() else "Unknown"}',
                            'description': parts[3].strip() if len(parts) > 3 else 'Style violation',
                            'line_number': int(parts[1]) if parts[1].isdigit() else None,
                            'severity': 'low',
                            'type': 'style'
                        })
        except Exception as e:
            style_issues.append({
                'title': 'Style Analysis Error',
                'description': f'Could not run style analysis: {str(e)}',
                'severity': 'info',
                'type': 'style'
            })
        
        return style_issues
    
    def _basic_js_analysis(self, code_content):
        """Basic JavaScript analysis"""
        issues = []
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for common issues
            if 'eval(' in line:
                issues.append({
                    'title': 'Dangerous eval() usage',
                    'description': 'Using eval() can be dangerous and should be avoided',
                    'line_number': i,
                    'severity': 'high',
                    'type': 'security'
                })
            
            if 'document.write(' in line:
                issues.append({
                    'title': 'document.write usage',
                    'description': 'document.write can cause issues and should be avoided',
                    'line_number': i,
                    'severity': 'medium',
                    'type': 'best_practice'
                })
        
        return issues
    
    def _ai_code_review(self, code_content, language):
        """Use OpenAI to analyze code"""
        ai_issues = []
        try:
            prompt = f"""
            Analyze this {language} code for potential issues. Return a JSON array of issues with this format:
            [
                {{
                    "title": "Issue title",
                    "description": "Detailed description",
                    "severity": "low|medium|high|critical",
                    "type": "security|bug|performance|best_practice",
                    "line_number": number or null,
                    "suggestion": "How to fix this issue"
                }}
            ]
            
            Code to analyze:
            ```{language}
            {code_content[:2000]}  # Limit code length for API
            ```
            
            Focus on: security vulnerabilities, potential bugs, performance issues, and code quality violations.
            Return only valid JSON, no other text.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a code review expert. Analyze code and return issues in JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                # Remove markdown code blocks if present
                if ai_response.startswith('```'):
                    ai_response = re.sub(r'```[a-zA-Z]*\n?', '', ai_response)
                
                parsed_issues = json.loads(ai_response)
                if isinstance(parsed_issues, list):
                    ai_issues = parsed_issues
                else:
                    ai_issues = [parsed_issues] if isinstance(parsed_issues, dict) else []
            except json.JSONDecodeError:
                ai_issues.append({
                    'title': 'AI Analysis Available',
                    'description': ai_response[:500] + '...' if len(ai_response) > 500 else ai_response,
                    'severity': 'info',
                    'type': 'best_practice'
                })
                
        except Exception as e:
            ai_issues.append({
                'title': 'AI Analysis Error',
                'description': f'Could not complete AI analysis: {str(e)}',
                'severity': 'info',
                'type': 'best_practice'
            })
        
        return ai_issues