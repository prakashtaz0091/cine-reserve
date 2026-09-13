from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .tasks import send_email_verification_mail
from .models import OTP
from django.contrib import messages
from django_ratelimit.decorators import ratelimit


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