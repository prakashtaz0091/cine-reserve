from datetime import timedelta, datetime
from django.utils import timezone
from core.models import Show


def create_shows(start_date_str, end_date_str, halls, times, price, movie_id):
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    else:
        start_date = None

    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = None
    
    delta = timedelta(days=1)
    count = 0
    for hall in halls:
        current_date = start_date
        while current_date <= end_date:
            for time in times:
                show_time = datetime.strptime(f"{str(current_date)} {time}", '%Y-%m-%d %H:%M')
                
                # Convert naive datetime to Django-aware datetime
                show_time = timezone.make_aware(
                    show_time,
                    timezone.get_current_timezone()
                )

                show, created = Show.objects.get_or_create(
                    movie_id=movie_id,
                    cinemahall_id=hall,
                    show_time=show_time,
                    defaults={
                        'price':price
                    }
                )
                if created:
                    count += 1
            
            current_date += delta
            
    return count