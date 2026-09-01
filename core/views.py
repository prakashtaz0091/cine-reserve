from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Show, Reservation, Seat
from django.utils import timezone
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.db import IntegrityError, transaction
from django.contrib import messages


@login_required
def hall_seats_view(request, show_id):
    
    if request.method == "POST":
        form_show_id = request.POST.get('show')
        form_seats = request.POST.get('seats')
        seats_ids = form_seats.split(',')  
        
        try:
            with transaction.atomic():
                show = Show.objects.get(pk=form_show_id)
                for seat_id in seats_ids:
                    seat = Seat.objects.get(pk=seat_id)
                    Reservation.objects.create(
                        show=show,
                        seat=seat,
                        customer=request.user
                    )
        except IntegrityError:
            messages.error(request, "One of these seats has just been reserved by another customer")
            return redirect("hall_seats", show_id=show_id)  
        except Seat.DoesNotExist:
            messages.error(request, "Incorrect seat selection")
            return redirect("hall_seats", show_id=show_id)  
            
            
        
        messages.success(request, "Seats has been selected successfully, please continue to payment")
        return redirect("movie_list")
        
    
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