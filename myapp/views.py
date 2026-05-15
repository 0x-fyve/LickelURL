from django.shortcuts import render, redirect, get_object_or_404
from .models import ShortURL, ClickEvent
import random, string
import requests
from django.contrib.auth.models import  auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from user_agents import parse
from collections import Counter


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

    user_agent_string = request.META.get(
        "HTTP_USER_AGENT",
        ""
    )

    user_agent = parse(user_agent_string)

    if user_agent.is_mobile:
        device = "Mobile"

    elif user_agent.is_tablet:
        device = "Tablet"

    else:
        device = "Desktop"

    browser = user_agent.browser.family

    ClickEvent.objects.create(
        short_url=urlobject,
        device=device,
        browser=browser,
        ip_address=request.META.get("REMOTE_ADDR")
    )

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

@login_required
def dashboard(request):
    user = request.user
    if request.method == "POST":
        original_url = request.POST.get('long_url')
        custom_alias = request.POST.get("custom_alias")

        # use custom alias if provided
        if custom_alias:
            code = custom_alias

            if ShortURL.objects.filter(short=code).exists():

                return render(request, "dashboard.html", {
                    "error": "Alias already exists"
                })

        else:
            code = generate_short_code()

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

    click_events = ClickEvent.objects.filter(
        short_url__user=request.user
    )

    device_counts = Counter(
        click_events.values_list(
            "device",
            flat=True
        )
    )
    mobile = device_counts.get("Mobile", 0)
    desktop = device_counts.get("Desktop", 0)
    tablet = device_counts.get("Tablet", 0)

    total_devices = mobile + desktop + tablet

    mobile_percent = round(
        (mobile / total_devices) * 100
    ) if total_devices else 0

    desktop_percent = round(
        (desktop / total_devices) * 100
    ) if total_devices else 0

    tablet_percent = round(
        (tablet / total_devices) * 100
    ) if total_devices else 0   

    browser_counts = Counter(
        click_events.values_list(
            "browser",
            flat=True
        )
    )

    top_browsers = browser_counts.most_common(5)
    context = {
        "urls": urls,
        "recent_links": recent_links,

        "total_links": total_links,
        "total_clicks": total_clicks,
        "active_links": active_links,
        "mobile_percent": mobile_percent,
        "desktop_percent": desktop_percent,
        "tablet_percent": tablet_percent,

        "top_browsers": top_browsers,
    }

    return render(request, "dashboard.html", context)