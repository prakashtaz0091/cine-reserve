from celery import shared_task
from .models import Reservation
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import render_to_string


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
# def send_receipt_in_mail(reservation_detail_url, full_name, user_email):
    
    
#     send_mail(
#         "Reservation Success",
#         f"""Hello, {full_name} !
#         Your show reservation is completed successfully. 
#         Please use the given link to see reservation details or download receipt
        
#         {reservation_detail_url}
#         """,
#         settings.DEFAULT_FROM_EMAIL,
#         [user_email, "dip.mind@outlook.com", "raydinesh2014@gmail.com", "veyola3213@94an.com"],
#         fail_silently=False,
#     )


@shared_task
def send_receipt_in_mail(reservation_detail_url, full_name, user_email):
    html_content = render_to_string(
        "email/reservation-success-mail.html",
        {
            "full_name": full_name,
            "reservation_detail_url": reservation_detail_url,
        },
    )

    email = EmailMultiAlternatives(
        subject="Reservation Success",
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            user_email,
        ],
    )

    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
