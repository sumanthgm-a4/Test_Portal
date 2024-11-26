import io
import sys
import subprocess
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# Create your views here.

def render_home(request):
    return render(request, "index.html")

def render_login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('home')
    if request.method == "POST":
        a = request.POST.get("username")
        b = request.POST.get("password")
        auth = authenticate(request, username=a, password=b)
        if auth:
            login(request, auth)
            return redirect('home')
        else:
            messages.error(request, "Please enter correct login credentials")
            return render(request, "login.html")
    return render(request, "login.html")

def render_register(request):
    if request.method == "POST":
        firstname = request.POST.get('fname')
        lastname = request.POST.get('lname')
        email = request.POST.get('mailid')
        username = request.POST.get('username')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')
        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists")
            return redirect('register')
        if len(password) < 8:
            messages.error(request, "Password must have 8 or more characters")
            return redirect('register')
        if password.isalnum():
            messages.error(request, "Password must have at least one special character")
            return redirect('register')
        if password != cpassword:
            messages.error(request, "Passwords don't match")
            return redirect('register')
        
        new_user = User(username=username, first_name=firstname, last_name=lastname, email=email)
        new_user.set_password(password)
        new_user.save()
        messages.success(request, "User successfully created")
        return redirect('login')
    return render(request, "register.html")

@login_required
def render_logout(request):
    logout(request)
    messages.info(request, "You are successfully logged out")
    return redirect('login')

@login_required
def render_test_page(request):
    return render(request, "test.html")

@csrf_exempt
def run_code(request):
    if request.method == "POST":
        # Parse incoming JSON data for the 'code' field
        try:
            data = json.loads(request.body.decode('utf-8'))
            code = data.get('code', None)  # Get 'code' from JSON payload

            if not code:
                return JsonResponse({'error': 'No code provided'}, status=400)

            # Test cases
            test_cases = [
                {'input': 5, 'expected': 120},
                {'input': 3, 'expected': 6},
                {'input': 10, 'expected': 3628800},
                {'input': 0, 'expected': 1},
                {'input': 1, 'expected': 1},
                {'input': 2, 'expected': 2},
                {'input': 15, 'expected': 1307674368000},
            ]

            failed_test_count = 0
            results = []

            for test_case in test_cases:
                input_value = test_case['input']
                expected_output = test_case['expected']

                print(code)
                
                # Prepare the code to include the solve_factorial function
                code_with_input = f"""
def solve_factorial(n):
    # User-provided function code goes here
    {code}

# Now we run the solve_factorial function with the input_value
print(solve_factorial({input_value}))
                """

                print(code_with_input)
                
                # Execute the code in a separate process
                code_output = execute_code(code_with_input)
                if code_output != str(expected_output):
                    failed_test_count += 1
                results.append({'input': input_value, 'expected': expected_output, 'output': code_output})

            return JsonResponse({
                'output': f"Test Results: {results}",
                'error': None,
                'failed_count': failed_test_count
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

def execute_code(code):
    try:
        # Execute the code in a subprocess and capture the output
        process = subprocess.Popen(
            ['python3', '-c', code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Get the output from the process
        stdout, stderr = process.communicate()

        # Log the output for debugging
        print("STDOUT: ", stdout.decode('utf-8'))  # This will log the actual output
        print("STDERR: ", stderr.decode('utf-8'))  # This will log any errors

        if stderr:
            return f"Error: {stderr.decode('utf-8')}"

        return stdout.decode('utf-8').strip()
    except Exception as e:
        return f"Error: {str(e)}"
