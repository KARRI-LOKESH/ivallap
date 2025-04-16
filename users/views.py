import random
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib import messages as django_messages
from django.shortcuts import redirect
from posts.models import Post 
from django.http import HttpResponse
from django.views.generic import TemplateView
from posts.forms import CustomUserCreationForm,UserProfileUpdateForm,MessageForm
from django.db.models import Q
# User Signup View
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if not user.username:
                user.username = user.email.split("@")[0] + str(random.randint(1000, 9999))

            user.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Error in sign-up form. Please check the fields.")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})

# Login View
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Email not found!")
            return redirect("login")

        # Generate OTP
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.save()

        # Send OTP via email
        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            "karrilokesh108@example.com",
            [email],
            fail_silently=False,
        )

        # Store email in session for OTP verification
        request.session["email"] = email
        return redirect("verify_otp")

    return render(request, "users/login.html")

# OTP Verification View
def verify_otp(request):
    if request.method == "POST":
        email = request.session.get("email")
        otp_entered = request.POST.get("otp")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid OTP verification process!")
            return redirect("login")

        if user.otp == otp_entered:
            login(request, user)
            messages.success(request, "OTP Verified. Welcome!")
            return redirect("profile")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("verify_otp")

    return render(request, "users/verify_otp.html")



User = get_user_model()

@login_required
def profile_view(request, username=None):
    if not username:
        if request.user.is_authenticated and request.user.username:
            return redirect("user-profile", username=request.user.username)
        else:
            return redirect("login")
    user_profile = get_object_or_404(User, username=username)

    followers_count = user_profile.followers.count()
    following_count = user_profile.following.count()
    posts = Post.objects.filter(user=user_profile)

    # Check if the logged-in user is following this profile
    is_following = request.user.following.filter(id=user_profile.id).exists()

    if request.method == "POST":
        if request.user == user_profile:
            form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect("user-profile", username=user_profile.username)
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            messages.error(request, "You can only edit your own profile.")
            return redirect("user-profile", username=request.user.username)
    else:
        form = UserProfileUpdateForm(instance=user_profile)

    return render(request, "users/profile.html", {
        "form": form,
        "followers_count": followers_count,
        "following_count": following_count,
        "posts": posts,
        "user_profile": user_profile,
        "is_following": is_following,  # Pass is_following to the template
    })
# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")

@login_required
def update_profile(request):
    user = request.user

    if request.method == "POST":
        print("🟢 Received a POST request")  
        print("Received POST data:", request.POST)  # ✅ Log full POST data
        
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")

            # 🔵 Check if redirect_choice exists
            redirect_choice = request.POST.get("redirect", None)
            print(f"🔵 Redirect Choice: {redirect_choice}")  

            if redirect_choice == "create":
                print("🟢 Redirecting to post-create...")
                return redirect("post-create")  
            elif redirect_choice == "list":
                print("🟢 Redirecting to post-list...")
                return redirect("post-list")  

            print("🔴 No valid redirect choice, going back to profile...")
            return redirect("profile")  # Default if no button was clicked

        else:
            print("🔴 Form is invalid", form.errors)  

    else:
        print("🟡 GET request received (not a POST request)")

    form = UserProfileUpdateForm(instance=user)
    return render(request, "users/profile.html", {"form": form})
class EntryPageView(TemplateView):
    template_name = "users/entry.html"  # ✅ Correct path
def home(request):
    return render(request, "users/entry.html") 
def about(request):
    return render(request, "users/about.html") 
def base(request):
    return render(request, "users/base.html") 
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        full_message = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}"

        send_mail(
            subject=f"New Contact Form Submission: {subject}",
            message=full_message,
            from_email=email,
            recipient_list=['karrilokesh108@gmail.com'],
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')  # Ensure 'contact' URL name is mapped correctly in `urls.py`

    return render(request, 'users/contact.html')
@login_required
def my_posts(request):
    user_posts = Post.objects.filter(user=request.user)
    return render(request, 'users/my_posts.html', {'posts': user_posts})


@login_required
def follow_unfollow(request, user_id):
    user_to_follow = get_object_or_404(CustomUser, id=user_id)
    
    if request.user != user_to_follow:
        if request.user.following.filter(id=user_id).exists():
            request.user.following.remove(user_to_follow)
            messages.success(request, f"You unfollowed {user_to_follow.username}.")
        else:
            request.user.following.add(user_to_follow)
            messages.success(request, f"You are now following {user_to_follow.username}.")
    
    return redirect("user-profile", username=user_to_follow.username)
User = get_user_model()

def search_users(request):
    query = request.GET.get("query", "").strip()
    users = User.objects.filter(username__icontains=query) if query else []

    # Fetch posts of the searched users
    posts = Post.objects.filter(user__in=users).select_related("user")

    return render(request, "users/search.html", {
        "users": users,
        "posts": posts,
    })
def followers_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    followers = user.followers.all()
    return render(request, 'users/followers_list.html', {'user': user, 'followers': followers})

def following_list(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    following = user.following.all()
    return render(request, 'users/following_list.html', {'user': user, 'following': following})


