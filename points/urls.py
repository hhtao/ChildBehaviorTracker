# points/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get_points/', views.get_points, name='get_points'),
    path('get_points_data/', views.get_points_data, name='get_points_data'),
]