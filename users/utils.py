import pyotp
from django.core.mail import send_mail

def generate_otp():
    """Generate a 6-digit OTP"""
    totp = pyotp.TOTP(pyotp.random_base32())
    return totp.now()

def send_otp_email(email, otp):
    """Send OTP via email"""
    subject = "Your OTP for Login"
    message = f"Your One-Time Password (OTP) is: {otp}. Use this to log in."
    send_mail(subject, message, "your_email@gmail.com", [email])
