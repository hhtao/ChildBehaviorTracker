#behaviours/urls.py
from django.urls import path
from . import views
from .views import BehaviorRecordListCreateAPIView

urlpatterns = [
    path('', views.index, name='behv_index'),
    path('api/behaviorrecords/', BehaviorRecordListCreateAPIView.as_view(), name='behaviorrecord-list-create'),
]