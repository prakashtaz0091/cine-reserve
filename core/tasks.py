from celery import shared_task
from .models import Reservation
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse


@shared_task
def cleanup_expired_and_cancelled_reservations():
    deleted_count, _ = Reservation.objects.filter(
        status=Reservation.STATUS_CHOICES.cancel
    ).delete()
    
    now = timezone.now()
    expired_delete_count, _ = Reservation.objects.filter(
        status=Reservation.STATUS_CHOICES.pending,
        expires_at__lte=now
    ).delete()
    
    return deleted_count, expired_delete_count


# @shared_task
def send_receipt_in_mail(request, master_id):
    
    reservation_url = request.build_absolute_uri(
        reverse("reservation_detail", kwargs={"pk": master_id})
    )
    send_mail(
        "Reservation Success",
        f"""Hello, {request.user.get_full_name()} !
        Your show reservation is completed successfully. 
        Please use the given link to see reservation details or download receipt
        
        {reservation_url}
        """,
        "from@example.com",
        ["to@example.com"],
        fail_silently=False,
    )
    