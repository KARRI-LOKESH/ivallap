import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .models import CustomUser
from posts.models import Post 
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm,UserProfileUpdateForm

# User Signup View
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
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
            return redirect("profil")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("verify_otp")

    return render(request, "users/verify_otp.html")

# Profile View (After Login)
@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profil")  # ✅ Ensuring an HTTP response is returned
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(request, "users/profil.html", {"form": form}) 
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
            return redirect("profil")  # Default if no button was clicked

        else:
            print("🔴 Form is invalid", form.errors)  

    else:
        print("🟡 GET request received (not a POST request)")

    form = UserProfileUpdateForm(instance=user)
    return render(request, "users/profil.html", {"form": form})
class EntryPageView(TemplateView):
    template_name = "users/entry.html"  # ✅ Correct path
