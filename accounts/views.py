from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings


@login_required
@require_POST
def verify_email_initiate(request):
    otp = "123456"
    send_mail(
        subject="Email Verification",
        message=f"Please verify your email with link given below and given OTP {otp}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email]   
        )
    
    return redirect("profile")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")    


@login_required
def logout_view(request):
    logout(request)
    return redirect("movie_list")