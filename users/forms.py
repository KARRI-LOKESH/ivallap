from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Message

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'name', 'email', 'age', 'phone', 'profile_pic', 'username', 'bio',
            'first_name', 'last_name', 'gender', 'location', 'linkedin', 'github'
        ]

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'profile_pic', 'bio', 'first_name', 'last_name', 'gender', 
            'location', 'linkedin', 'github'
        ]

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver', 'content']
