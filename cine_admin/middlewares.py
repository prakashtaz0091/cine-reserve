from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import redirect


class AdminRoutesProtectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        if "cine-admin" in request.path:
            if not request.user.is_authenticated: 
                messages.error(request, "Please login first")
                return redirect("login")
            
            if not request.user.groups.filter(name="AdminStaff").exists():
                messages.error(request, "You are not authorized to access this page")
                return redirect("movie_list")
                
        response = self.get_response(request)

        return response