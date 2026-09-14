from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.urls import reverse
from .tasks import send_email_verification_mail, send_password_reset_mail
from .models import OTP
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def password_reset_view(request):
    if request.method == "POST":
        print(request.POST)
        otp_value = request.POST.get('otp')
        new_password = request.POST.get('password') 
        new_cpassword = request.POST.get('c-password') 
        
        # Check OTP validity
        try:
            otp = OTP.objects.get(value=otp_value)
        except OTP.DoesNotExist():
            messages.error(request, "Invalid OTP")
            return redirect("password_reset_view")
        except OTP.MultipleObjectsReturned():
            messages.error(request, "Something went wrong with OTP, please request new otp")
            return redirect("login")
            
        
        # check if otp is expired
        if otp.is_expired:
            messages.error(request, "OTP has been expired.")
            return redirect("login")
        
        # check if newpassword and confirm new password matches
        if new_password != new_cpassword:
            messages.error(request, "New password and Confirm New password doesn't match.")
            return redirect("password_reset_view")
        
        # check listed password validation
        try:
            validate_password(new_password)
            print("Password is valid")
        except ValidationError as e:
            str_error_message = "\n".join(e.messages)
            messages.error(request, str_error_message)
            return redirect("password_reset_view")
        
        otp.user.set_password(new_password)
        otp.user.save()
        messages.success(request, "Password reset successful, please continue via login")
        
        return redirect("login")
    
    return render(request, "accounts/reset-password.html")


def forgot_password_view(request):
    if request.method == "POST":
        username_value = request.POST.get("username")
        
        url = request.build_absolute_uri(
            reverse("password_reset_view")
        )
        send_password_reset_mail.delay(username=username_value, reset_url=url)
        
        messages.success(request, "If username exists, password reset link with OTP has been sent to respective email")
        return redirect("movie_list")       
    
    
    return render(request, "accounts/forgot-password.html")


@login_required
def verify_email_otp(request):
    if request.method == "POST":
        otp_value = request.POST.get("otp")
        try:
            otp = OTP.objects.get(value=otp_value, user=request.user)
        except OTP.DoesNotExist():
            messages.error(request, "Invalid OTP")
            return redirect("verify_email_otp")
        
        if otp.is_expired:
            messages.error(request, "OTP expired. Please request new otp")
            return redirect("profile")
        
        otp.user.profile.is_verifed = True
        otp.user.profile.save()
        return redirect("profile")
            
    return render(request, "accounts/verify_otp.html")


@login_required
@require_POST
@ratelimit(key="user", rate="1/2m", method="POST", block=False)
def verify_email_initiate(request):
    
    if getattr(request, "limited", False):
        messages.warning(
            request,
            "A verification email was recently sent. "
            "Please wait 2 minutes before requesting another one.",
        )
        return redirect("profile")


    url = request.build_absolute_uri(
        reverse("verify_email_otp")
    )
    
    send_email_verification_mail.delay(request.user.username, url)
    
    return redirect("profile")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")    


@login_required
def logout_view(request):
    logout(request)
    return redirect("movie_list")