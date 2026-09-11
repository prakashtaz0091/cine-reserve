from django.shortcuts import render, redirect, get_object_or_404
from core.models import Cinema, CinemaHall, Seat, Movie, MasterReservation
from django.http  import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from .services import create_shows


def reservation_qr_verification(request):
    if request.method == "POST":
        master_id = request.POST.get('master_id')
        try:
            master = get_object_or_404(MasterReservation, pk=master_id)
        except Exception:
            return HttpResponse("<h1> Ticket doesn't exist </h1>")
            
        context = {
            'movie_name': master.show.movie.name,
            'show_time': master.show.show_time,
            'seats': Seat.objects.filter(reservations__in=master.reservations.all())
        }
        if master:
            return render(request, "core/ticket.html", context)
        else:
            return HttpResponse("<h1> Ticket doesn't exist </h1>")
        
        
    return render(request, "core/qr-verification.html")


def show_setup(request):
    
    if request.method == "POST":
        print(request.POST)
        movie_id = request.POST.get('movie')
        price = request.POST.get('price')
        halls = request.POST.getlist('halls')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        times = request.POST.getlist('times')

        created_count = create_shows(
            start_date_str=start_date_str,
            end_date_str=end_date_str,
            price=price,
            halls=halls,
            times=times,
            movie_id=movie_id
        )
        if created_count>0:
            messages.success(request, f"{created_count} show(s) created successfully")
        else:
            messages.error(request, "No shows created.")
        
        return redirect("show_setup")
    
    movies = Movie.objects.all()
    cinemas = Cinema.objects.all()
    cinema_halls = CinemaHall.objects.filter(cinema=cinemas.first())
    
    context = {
        'movies':movies,
        'cinemas':cinemas,
        'halls':cinema_halls   
    }
    return render(request, "cine_admin/show-setup.html", context)

def get_hall_seats(request):
    hall_id = request.GET.get("hall")
    hall = CinemaHall.objects.get(pk=hall_id)
    seats = Seat.objects.filter(cinemahall=hall)
    html = render_to_string('cine_admin/seats-setup-partial.html', {'seats': seats, 'hall':hall})
    
    return HttpResponse(html)


def get_cinema_halls_multiselect(request):
    cinema_id = request.GET.get("cinema")
    halls = CinemaHall.objects.filter(cinema_id=cinema_id)
    html = render_to_string('cine_admin/hall-multi-select-partial.html', {'halls': halls})
    
    return HttpResponse(html)


def get_cinema_halls(request):
    cinema_id = request.GET.get("cinema_id")
    halls = CinemaHall.objects.filter(cinema_id=cinema_id)
    html = render_to_string('cine_admin/hall-select-partial.html', {'halls': halls})
    
    return HttpResponse(html)


def hall_seat_setup(request):
    
    if request.method == "POST":
        # print(request.POST)
        post_data = request.POST
        hall_id = post_data.get('hall')
        seat_names = post_data.getlist('seat')
        row = int(post_data.get('row'))
        col = int(post_data.get('col'))
        
        hall = CinemaHall.objects.get(pk=hall_id)
        if not (hall.row >= row or hall.col >= col):
            hall.row = row
            hall.col = col
            hall.save()
        else:
            messages.warning(request, "No. of rows and columns can be increased but currently cannot be decreased")
        created_count = 0
        for seat in seat_names:
            seat, created = Seat.objects.get_or_create(
                name=seat,
                defaults={
                    'cinemahall_id':hall_id
                }
            )
            if created:
                created_count += 1
                
        print(f"New seats created for hall {hall_id} are {created_count}")
        
        return redirect("hall_seat_setup")
    
    cinemas = Cinema.objects.all()
    first_cinema = cinemas.first()
    halls = CinemaHall.objects.filter(cinema=first_cinema)
    first_hall = halls.first()
    seats = Seat.objects.filter(cinemahall=first_hall)
    seats = sorted(
        seats,
        key=lambda seat: (seat.name[0],int(seat.name[1:]))
        )
    
    context = {
        'cinemas': cinemas,
        'halls': halls,
        'seats': seats,
        'hall':first_hall
    }
    
    return render(request, "cine_admin/hall-seats-setup.html", context)