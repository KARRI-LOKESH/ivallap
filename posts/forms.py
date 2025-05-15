
from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from posts.models import Message,Story,Comment
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            'name', 'email', 'age', 'phone', 'username','gender', 
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
class StoryUploadForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['media', 'caption']
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
