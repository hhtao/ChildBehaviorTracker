#home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('record/', views.record, name='record'),
    path('get_indicators/', views.get_indicators, name='get_indicators'),
    path('get_actions/<int:indicator_id>/', views.get_actions, name='get_actions'),
    path('record_action/', views.record_action, name='record_action'),
]