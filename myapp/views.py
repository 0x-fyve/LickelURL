from django.shortcuts import render, redirect, get_object_or_404
from .models import ShortURL
import random, string
import requests
from django.contrib.auth.models import  auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.
def create_shorturl():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    while ShortURL.objects.filter(short=code).exists():
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def index(request):
    code = []
    qr_code = []
    if request.method == 'POST':
        action = request.POST.get('action') 
        original_url = request.POST.get('long_url')
        if action == 'shorten':
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

            while ShortURL.objects.filter(short=code).exists():
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))


            if request.user.is_authenticated:
                user = request.user
            else:
                user = None

            ShortURL.objects.create(
                user=user,
                original_url=original_url,
                short=code
            )
            
        elif action == 'qr':
            qr_code = f"http://api.qrserver.com/v1/create-qr-code/?data={original_url}&size=200x200"

    return render(request, 'index.html', {"code":code, "qr_code_url":qr_code} )


def redirect_url(request, url):
    urlobject = get_object_or_404(ShortURL, short=url)
    urlobject.clicks += 1

    urlobject.save()

    return redirect(urlobject.original_url)

User = get_user_model()

def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        confirm = request.POST.get('confirm')
        
        if password == confirm:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already in use')
                return redirect('signup')   
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                user.save()
                messages.info(request, 'Account created succesfully')
                return redirect('login')
            
        else:
            messages.error(request, "Passwords do not match")
            return redirect("signup")
     
    return render(request, 'signup.html')        
            

def login_view(request):

    if request.method == "POST":
        user = []

        email = request.POST.get("email")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is not None:
            login(request, user)

            messages.success(request, "Login successful")
            return redirect("dashboard")

        else:
            messages.error(request, "Invalid email or password")
            return redirect("login")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def dashboard(request):
    return render(request, "dashboard.html")