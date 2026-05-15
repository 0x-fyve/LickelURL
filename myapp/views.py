from django.shortcuts import render, redirect, get_object_or_404
from .models import ShortURL
import random, string
import requests
from django.contrib.auth.models import  auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

# Create your views here.
def generate_short_code():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    while ShortURL.objects.filter(short=code).exists():
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return code    

def index(request):
    code = []
    qr_code = []
    if request.method == 'POST':
        action = request.POST.get('action') 
        original_url = request.POST.get('long_url')
        if action == 'shorten':
            code =  generate_short_code()

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
    user = request.user
    if request.method == "POST":
        original_url = request.POST.get('long_url')
        custom_alias = request.POST.get("custom_alias")

        # use custom alias if provided
        if custom_alias:

            short = custom_alias

        else:

            code = generate_short_code()

            if ShortURL.objects.filter(short=short).exists():

                return render(request, "dashboard.html", {
                    "error": "Alias already exists"
                })

        ShortURL.objects.create(
                user=request.user,
                original_url=original_url,
                short=code
            )
        return redirect("dashboard")
    
    urls = ShortURL.objects.filter(user=request.user).order_by("-created_at")

    total_links = urls.count()
    
    total_clicks = urls.aggregate(
        total=Sum("clicks")
    )["total"] or 0

    active_links = urls.filter(
        clicks__gt=0
    ).count()

    recent_links = urls[:5]

    context = {
        "urls": urls,
        "recent_links": recent_links,

        "total_links": total_links,
        "total_clicks": total_clicks,
        "active_links": active_links,
        
    }

    return render(request, "dashboard.html", context)