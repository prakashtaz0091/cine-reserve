from rest_framework import serializers
from core.models import Movie, Cinema, CinemaHall


class MovieModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        # fields = "__all__"
        fields = ["id", "name", "release_date"]
        
        
class CinemaHallModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CinemaHall
        fields = "__all__"
        
        
class CinemaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = "__all__"
        
        
class CinemaModelDetailSerializer(serializers.ModelSerializer):
    halls = CinemaHallModelSerializer(many=True)
    class Meta:
        model = Cinema
        fields = "__all__"