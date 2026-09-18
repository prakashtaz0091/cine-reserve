from django.db import models
from django.contrib.auth.models import User
import secrets
from django.utils import timezone
from datetime import timedelta


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def get_expiry():
    return timezone.now() + timedelta(minutes=30)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_verifed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to="profile_photos/", null=True)
    
    def __str__(self):
        return self.user.username
    


class OTP(models.Model):
    value = models.CharField(max_length=6, default=generate_otp)
    expires_at = models.DateTimeField(default=get_expiry)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    
    def __str__(self):
        return f"{self.value}->{self.user.email}"
    
    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()