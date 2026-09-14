from django.urls import path
from .import views


urlpatterns = [
    path('profile/', views.profile_view, name="profile"),
    path('logout/', views.logout_view, name="logout"),
    path('verify/email/', views.verify_email_initiate, name="verify_email_initiate"),
    path('verify/email/otp/', views.verify_email_otp, name="verify_email_otp"),
    
    path('forgot-password/', views.forgot_password_view, name="forgot_password_view"),
    path('reset-password/', views.password_reset_view, name="password_reset_view"),
    
]
