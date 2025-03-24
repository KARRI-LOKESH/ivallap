from django.urls import path
from .views import signup_view, login_view, verify_otp, logout_view, profile_view
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.shortcuts import render

from . import views
urlpatterns = [
    path("entry/", TemplateView.as_view(template_name="users/entry.html"), name="landing-page"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profil"),
    path("home/", views.home, name="home"), 
    path("about/", views.about, name="about"),
    path("contact", views.contact, name="contact"),  
]
