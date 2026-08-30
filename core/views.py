from django.shortcuts import render, redirect
from .models import Movie, Show
from django.utils import timezone
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required



def home(request):
    
    latest_movies = Movie.objects.order_by("-release_date")[:8]
    # print(latest_movies)
    
    context = {
        'movies': latest_movies,
    }
    
    return render(request, "core/home.html", context)


@login_required
def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)
    shows = Show.objects.filter(movie=movie)
    # print(shows)
    context = {
        'movie': movie,
        'shows': shows,
        "from_date": timezone.now(),
    }
    return render(request, "core/movie_detail.html", context)
    

def register_view(request):
    if request.method == "POST":
        # print("REquest data: ", request.POST)
        form = RegisterForm(data=request.POST)
        
        if form.is_valid():
            data = form.cleaned_data
            User.objects.create_user(
                username=data.get('username'),
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            print("User creation successful")
            return redirect("login")
        else:
            return render(request, "core/register.html", {
                'form':form
            })
    
        
    return render(request, "core/register.html")


def login_view(request):
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print("Login sucessfull")
            return redirect("movie_list")         
    
    return render(request, "core/login.html")