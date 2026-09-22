from core.models import Movie, Cinema, MasterReservation, Reservation
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions, status
from django.db import IntegrityError, transaction
from django.conf import settings
from core.services import initiate_khalti_payment
from .filters import MovieFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend




# @api_view(["GET"])
# def movies(request):
#     movies = Movie.objects.all()
#     serializer = MovieModelSerializer(movies, many=True)
    
#     return Response(serializer.data)

class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieModelSerializer
    queryset = Movie.objects.all()
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = MovieFilter
    ordering_fields = ["name", "release_date"]


      
class CinemaViewSet(viewsets.ModelViewSet):
    queryset = Cinema.objects.all()
    
    def get_serializer_class(self):
        if self.action in "retrieve":
            return CinemaModelDetailSerializer
        
        return CinemaModelSerializer
    
    
class CinemaHallViewSet(viewsets.ModelViewSet):
    serializer_class = CinemaHallModelSerializer
    queryset = CinemaHall.objects.all()
    


class ProfileGetView(APIView):
    permission_classes = [permissions.IsAuthenticated]    
    def get(self, request, format=None):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        
        return Response(serializer.data)       


class ReserveShowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ShowReserveSerializer(data=request.data)

        if serializer.is_valid():
            
            show = serializer.validated_data["show"]
            seats = serializer.validated_data["seats"]
            print(show, seats)
            
            try:
                with transaction.atomic():
                    master = MasterReservation.objects.create(show=show)
                    for seat in seats:
                        Reservation.objects.create(
                            master_reservation=master,
                            show=show,
                            seat=seat,
                            customer=request.user
                        )
            except IntegrityError:
                return Response({
                    "status": "error",
                    "message": "One of these seats has just been reserved by another customer"
                }, status=status.HTTP_400_BAD_REQUEST)
                
                
            amount = show.price * len(seats) * 100 # paisa
            pidx, payment_url = initiate_khalti_payment(
                request=request,
                master=master,
                amount=amount
            )
            
            master.pidx = pidx
            master.amount = amount
            master.save()
            
            data = serializer.data
            data["payment_url"] = payment_url
            
            return Response(
                {
                    "status": "success",
                    "message": f"Seats reserved for {settings.RESERVATION_WINDOW_TIME} minutes. Please confirm payment within given time",
                    "data": data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )