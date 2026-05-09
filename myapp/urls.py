from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('r/<str:url>', views.redirect_url, name='redirect_url'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('dashboard', views.dashboard, name='dashboard')

]

