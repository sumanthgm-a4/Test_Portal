from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# Create your views here.

def render_home(request):
    
    return render(request, "index.html")


def render_login(request):
    
    print(request.method)
    print(request.GET)
    print(request.POST)
    print(request.user)
    if request.user.is_authenticated:
        messages.warning(request, "You already logged in")
        return redirect('home')
    if request.method == "POST":
        a = request.POST.get("username")
        b = request.POST.get("password")
        print(a, b)
        result = User.objects.filter(username=a)
        print("User Exists? =", result)
        auth = authenticate(request, username=a, password=b)
        print("Valid Login Details? =", auth)
        if auth:
            login(request, auth)
            if request.user.is_superuser:
                print("Is Superuser")
                return redirect('/admin')
            messages.success(request, "You are successfully logged in")
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
        print(firstname, lastname, email, username, password, cpassword)
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists")
            return redirect('register')
        if len(password) < 8:
            messages.error(request, "Password must have 8 or more characters")
            return redirect('register')
        if password.isalnum():
            messages.error(request, "Password must have atleast one special character")
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