from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")    


@login_required
def logout_view(request):
    logout(request)
    return redirect("movie_list")