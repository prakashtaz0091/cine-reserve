from core.models import Movie, Cinema
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import viewsets



# @api_view(["GET"])
# def movies(request):
#     movies = Movie.objects.all()
#     serializer = MovieModelSerializer(movies, many=True)
    
#     return Response(serializer.data)

class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieModelSerializer
    queryset = Movie.objects.all()

      
class CinemaViewSet(viewsets.ModelViewSet):
    queryset = Cinema.objects.all()
    
    def get_serializer_class(self):
        if self.action in "retrieve":
            return CinemaModelDetailSerializer
        
        return CinemaModelSerializer
    
    
class CinemaHallViewSet(viewsets.ModelViewSet):
    serializer_class = CinemaHallModelSerializer
    queryset = CinemaHall.objects.all()