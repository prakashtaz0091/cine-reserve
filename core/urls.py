from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="movie_list"),
    path('movies/<pk>/', views.movie_detail, name="movie_detail")
]
