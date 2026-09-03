from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Movie(models.Model):
    name = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    release_date = models.DateField(null=True)
    poster = models.ImageField(upload_to="movie_posters/", null=True)
    
    def __str__(self):
        return self.name


class Cinema(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name+self.location

    
class CinemaHall(models.Model):
    cinema = models.ForeignKey(Cinema, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.cinema}-{self.name}"   


class Seat(models.Model):
    name = models.CharField(max_length=10)
    cinemahall = models.ForeignKey(CinemaHall, on_delete=models.CASCADE, related_name="seats")
    
    
    class Meta:
        unique_together = ("name", "cinemahall")
    
    def __str__(self):
        return self.name
    
    
class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    cinemahall = models.ForeignKey(CinemaHall, on_delete=models.PROTECT)
    show_time = models.DateTimeField()
    price = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ("cinemahall", "movie", "show_time")
    
    def __str__(self):
        return f"{self.movie} - {self.cinemahall}"


class MasterReservation(models.Model):
    pidx = models.CharField(max_length=60, help_text="Payment intiate id from khalti", default="")
    amount = models.PositiveIntegerField(default=0)
    transaction_id = models.CharField(max_length=60, default="")
    payment_status = models.CharField(max_length=20, default="")
    
    

class Reservation(models.Model):
    class STATUS_CHOICES(models.TextChoices):
        pending = 'pd', 'Pending'
        confirmed = 'cm', 'Confirmed'
        cancel = 'cl', 'Cancelled'
        expired = 'ex', 'Expired'
    
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reservations")
    show = models.ForeignKey(Show, on_delete=models.PROTECT, related_name="reservations") 
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name="reservations")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=STATUS_CHOICES.pending)
    
    master_reservation = models.ForeignKey(MasterReservation, on_delete=models.PROTECT, null=True, related_name="reservations")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    expires_at = models.DateTimeField(null=True)
    
    class Meta:
        unique_together = ("show", "seat")
        
    def __str__(self):
        return self.customer.first_name

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()

        self.expires_at = self.created_at + timedelta(
            minutes=settings.RESERVATION_WINDOW_TIME
            )

        super().save(*args, **kwargs)


