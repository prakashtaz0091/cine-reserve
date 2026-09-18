from rest_framework import serializers
from core.models import Movie, Cinema, CinemaHall, Seat, Show
from accounts.models import Profile
from django.contrib.auth.models import User


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
        
        

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email"]
        

class ProfileSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()
    class Meta:
        model = Profile
        fields = "__all__"
        
        
class ShowReserveSerializer(serializers.Serializer):
    show = serializers.PrimaryKeyRelatedField(queryset=Show.objects.all())
    seats = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=Seat.objects.all()
        )
    )
    
    
    