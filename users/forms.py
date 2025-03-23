from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "name", "age", "phone"]

# Custom Form for Updating User Profile
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "bio", "profile_pic"]
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["name", "age", "phone", "gender", "location", "bio", "profile_pic", "linkedin", "github"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "linkedin": forms.URLInput(attrs={"placeholder": "LinkedIn Profile URL"}),
            "github": forms.URLInput(attrs={"placeholder": "GitHub Profile URL"}),
        }