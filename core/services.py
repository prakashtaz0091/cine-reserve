import json
import requests
from django.conf import settings
from .models import MasterReservation, Reservation
from django.db import transaction
from django.contrib import messages


def khalti_payment_lookup(request, pidx, purchase_order_id):
    try:
        master = MasterReservation.objects.get(pidx=pidx, pk=purchase_order_id)
    except MasterReservation.DoesNotExist:
        print("Something went wrong. Master reservation doesn't exist")
    except MasterReservation.MultipleObjectsReturned:
        print("Duplicate pidx exists")
        
    url = settings.KHALTI_LOOKUP_URL
    payload = json.dumps({
            "pidx": pidx
        })
    
    headers = {
        'Authorization': f'key {settings.KHALTI_API_SECRET_KEY}',
        'Content-Type': 'application/json',
        }

    response = requests.request("POST", url, headers=headers, data=payload)
    data_res = response.json()
    if data_res.get('status') == 'Completed':
        if int(data_res.get('total_amount')) == master.amount:  
            with transaction.atomic():
                master.transaction_id = data_res.get('transaction_id')
                master.payment_status = 'Completed'
                master.reservations.all().update(status=Reservation.STATUS_CHOICES.confirmed)
                master.save()
            
            messages.success(request, "Payment done and reservations confirmed")
            return master, True
            
        else:
            messages.error(request, "Amount mismatch, Reservation confirmation failed")
    else:
        print("Payment not completed, Reservation confirmation failed")
        
    return master, False


def initiate_khalti_payment(request, master, amount):
    url = settings.KHALTI_INITIATE_URL

    payload = json.dumps({
        "return_url": settings.KHALTI_RETURN_URL,
        "website_url": settings.WEBSITE_URL,
        "amount": str(amount),
        "purchase_order_id": str(master.id),
        "purchase_order_name": "Movie Ticket",
        "customer_info": {
            "name": request.user.get_full_name(),
            "email": request.user.email,
            "phone": "9800000001"
        }
    })
    headers = {
        'Authorization': f'key {settings.KHALTI_API_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    pidx = data.get("pidx")
    payment_url = data.get("payment_url")
    
    return pidx, payment_url