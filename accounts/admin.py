from django.contrib import admin
from .models import OTP, Profile

admin.site.register([OTP, Profile])