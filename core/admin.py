from django.contrib import admin
from .models import *


admin.site.register(Movie)
admin.site.register(Cinema)
admin.site.register(MasterReservation)


@admin.register(CinemaHall)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["name", "cinema"]
    
    
@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["name", "cinemahall"]
    
    
@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ["cinemahall", "movie", "show_time","price"]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["customer", "seat"]

