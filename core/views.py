from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Show, Reservation, Seat, MasterReservation, Cinema
from django.utils import timezone
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.conf import settings
from .services import initiate_khalti_payment, khalti_payment_lookup
from .tasks import send_receipt_in_mail
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from collections import OrderedDict


@login_required
def reservation_detail(request, pk):
    master = get_object_or_404(MasterReservation, pk=pk)
    # print(master.reservations.values_list('seat__name', flat=True))
    reserved_seats = master.reservations.values_list('seat__name', flat=True)
    amount_ruppes = master.amount/100
    context = {
        'master': master,
        'seats' : reserved_seats,
        'amount': amount_ruppes                
    }
    return render(request, "core/reservation-detail.html", context)


@login_required
def reservations(request):
    master_reservations = MasterReservation.objects.all()
    context = {
        'master_reservations': master_reservations
    }
    
    return render(request, "core/reservations.html", context)


@login_required
def verify_reservation_payment(request):
    data = request.GET 
    pidx = data.get('pidx')
    purchase_order_id = data.get('purchase_order_id')
    master, verified = khalti_payment_lookup(request=request, pidx=pidx, purchase_order_id=purchase_order_id)
    
    if verified:
        reservation_url = request.build_absolute_uri(
                reverse("reservation_detail", kwargs={"pk": master.id})
            )
        send_receipt_in_mail.delay(
            reservation_detail_url=reservation_url,
            master_id=str(master.id),
            full_name=request.user.get_full_name(),
            user_email=request.user.email,
        )
        return redirect("reservations")
    
    return redirect("movie_list")
        
    
@login_required
def hall_seats_view(request, show_id):
    
    if request.method == "POST":
        form_show_id = request.POST.get('show')
        form_seats = request.POST.get('seats')
        seats_ids = form_seats.split(',')  
        
        try:
            with transaction.atomic():
                show = Show.objects.get(pk=form_show_id)
                master = MasterReservation.objects.create(show=show)
                for seat_id in seats_ids:
                    seat = Seat.objects.get(pk=seat_id)
                    Reservation.objects.create(
                        master_reservation=master,
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
            
            
        
        messages.success(request, f"Seats reserved for {settings.RESERVATION_WINDOW_TIME} minutes. Please confirm payment within given time")
        
        amount = show.price * len(seats_ids) * 100 # paisa
        pidx, payment_url = initiate_khalti_payment(
            request=request,
            master=master,
            amount=amount
        )
        
        master.pidx = pidx
        master.amount = amount
        master.save()
        
        return redirect(payment_url)
        
    
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
    
    seats = sorted(
        seats,
        key=lambda seat: (seat.name[0],int(seat.name[1:]))
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


def get_shows_partial(request):
    cinema_id = request.GET.get('cinema')
    movie_id = request.GET.get('movie_id')

    if not cinema_id or not movie_id:
        shows_by_date = OrderedDict()
    else:
        shows = (
            Show.objects
            .filter(
                movie_id=movie_id,
                show_time__gt=timezone.now(),
            )
            .order_by('show_time')
        )

        shows_by_date = OrderedDict()

        for show in shows:
            # Convert to local time before extracting the date
            local_date = timezone.localtime(show.show_time).date()

            if local_date not in shows_by_date:
                shows_by_date[local_date] = []

            shows_by_date[local_date].append(show)

    context = {
        'shows_by_date': shows_by_date,
        'from_date': timezone.now(),
    }

    return HttpResponse(
        render_to_string(
            "core/shows-partial.html",
            context
        )
    )
    
    
def movie_detail(request, pk):
    movie = Movie.objects.get(pk=pk)
    cinemas = Cinema.objects.all()
    # print(shows[0].show_time, timezone.now())
    context = {
        'movie': movie,
        'cinemas':cinemas,
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