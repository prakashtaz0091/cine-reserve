from celery import shared_task
from .models import OTP
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


@shared_task
def send_password_reset_mail(username, reset_url):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist():
        print(f"User with username '{username}' doesn't exists")
    
    new_otp = OTP.objects.create(user=user)    
    
    send_mail(
        subject="Email Verification",
        message=f"""Please follow the link and continue resetting password
        {reset_url}
        
        OTP: {new_otp.value} 
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]   
        )



@shared_task
def send_email_verification_mail(username, verify_url):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist():
        print(f"User with username '{username}' doesn't exists")
    
    new_otp = OTP.objects.create(user=user)    
    
    send_mail(
        subject="Email Verification",
        message=f"""Please verify your email with link given below and given OTP {new_otp.value}
                    Click on this link to verify. {verify_url}
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]   
        )
    
    
@shared_task
def cleanup_expired_otps():
    deleted_count, _ = OTP.objects.filter(expires_at__lte=timezone.now()).delete()
    print(f"{deleted_count} expired otps were cleaned from db")
    