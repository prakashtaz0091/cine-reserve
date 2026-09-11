from django.urls import path
from .import views


urlpatterns = [
    path('profile/', views.profile_view, name="profile"),
    path('logout/', views.logout_view, name="logout"),
    path('verify/email/', views.verify_email_initiate, name="verify_email_initiate"),
]
