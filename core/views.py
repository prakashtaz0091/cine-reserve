from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Show, Reservation
from django.utils import timezone
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef



def hall_seats_view(request, show_id):
    show = get_object_or_404(Show, pk=show_id)
    # print(show.cinemahall.seat_set.all())
    # print(show.cinemahall.seats.all())
    seats = show.cinemahall.seats.annotate(
        reserved=Exists(
            Reservation.objects.filter(
                seat=OuterRef("pk"),
                show=show,
                status__in=[
                    Reservation.STATUS_CHOICES.confirmed,
                    Reservation.STATUS_CHOICES.pending
                ]
            )
        )
    )
    context = {
        'show':show,
        'seats':seats
    }
    return render(request, "core/hall_seats.html", context)
    


def home(request):
    
    latest_movies = Movie.objects.order_by("-release_date")[:8]
    # print(latest_movies)
    
    context = {
        'movies': latest_movies,
    }
    
    return render(request, "core/home.html", context)


def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)
    shows = Show.objects.filter(movie=movie, show_time__gt=timezone.now())
    # print(shows[0].show_time, timezone.now())
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