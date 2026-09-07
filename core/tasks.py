from io import BytesIO
from email.mime.image import MIMEImage
import qrcode
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


# @shared_task
# def send_receipt_in_mail(reservation_detail_url, master_id, full_name, user_email):
#     html_content = render_to_string(
#         "email/reservation-success-mail.html",
#         {
#             "full_name": full_name,
#             "reservation_detail_url": reservation_detail_url,
#         },
#     )

#     # Generate QR code in memory
#     qr = qrcode.QRCode(
#         version=None,
#         error_correction=qrcode.constants.ERROR_CORRECT_M,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(str(master_id))
#     qr.make(fit=True)

#     qr_image = qr.make_image()

#     # Store QR image in memory as PNG
#     qr_buffer = BytesIO()
#     qr_image.save(qr_buffer, format="PNG")
#     qr_buffer.seek(0)

#     email = EmailMultiAlternatives(
#         subject="Reservation Success",
#         body="",
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=[user_email, 'veyola3213@94an.com'],
#     )

#     email.attach_alternative(html_content, "text/html")

#     # Attach QR directly from memory
#     email.attach(
#         filename=f"reservation-{master_id}-qr.png",
#         content=qr_buffer.getvalue(),
#         mimetype="image/png",
#     )

#     email.send(fail_silently=False)


@shared_task
def send_receipt_in_mail(
    reservation_detail_url,
    master_id,
    full_name,
    user_email,
):
    # Generate QR code in memory
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )

    qr.add_data(str(master_id))
    qr.make(fit=True)

    qr_image = qr.make_image()

    # Store QR image in memory as PNG
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_content = qr_buffer.getvalue()

    # Render HTML email template
    html_content = render_to_string(
        "email/reservation-success-mail.html",
        {
            "full_name": full_name,
            "reservation_detail_url": reservation_detail_url,
            "qr_code_cid": "reservation_qr",
        },
    )

    email = EmailMultiAlternatives(
        subject="Reservation Success",
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[
            user_email,
            "veyola3213@94an.com",
            "prakashtaz0091@gmail.com"
        ],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    # Inline QR image for displaying directly in the HTML email
    inline_qr = MIMEImage(
        qr_content,
        _subtype="png",
    )

    inline_qr.add_header(
        "Content-ID",
        "<reservation_qr>",
    )

    inline_qr.add_header(
        "Content-Disposition",
        "inline",
        filename=f"reservation-{master_id}-qr.png",
    )

    email.attach(inline_qr)

    # Normal attachment for downloading
    email.attach(
        filename=f"reservation-{master_id}-qr.png",
        content=qr_content,
        mimetype="image/png",
    )

    email.send(
        fail_silently=False,
    )
