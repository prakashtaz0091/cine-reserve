from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_verifed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to="profile_photos/")
    
    def __str__(self):
        return self.user.username
    
