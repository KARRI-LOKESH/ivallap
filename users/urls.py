from django.urls import path
from .views import signup_view,contact_view,login_view, verify_otp, logout_view, profile_view,my_posts,follow_unfollow,search_users,followers_list,following_list
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.shortcuts import render

from . import views
urlpatterns = [
    path("entry/", TemplateView.as_view(template_name="users/entry.html"), name="landing-page"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),  
    path('profile/<str:username>/', profile_view, name='user-profile'),
    path("home/", views.home, name="home"), 
    path("about/", views.about, name="about"),
    path("base/", views.about, name="base"),
    path('contact/', contact_view, name='contact'),  
    path('my-posts/', my_posts, name='my-posts'),
    path('search/', search_users, name='search-users'),
    path('followers/<int:user_id>/', followers_list, name='followers-list'),
    path('following/<int:user_id>/', following_list, name='following-list'),
    path('follow/<int:user_id>/', follow_unfollow, name='follow-user'),
]
