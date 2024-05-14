# demo2/urls.py
from django.contrib import admin
from django.urls import path, include
from behaviours.views import BehaviorRecordListCreateAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # 首先包含home应用的URL配置
    path('home/', include('home.urls')),  
    path('api/behaviorrecords/', BehaviorRecordListCreateAPIView.as_view(), name='behaviorrecord-list-create'),
    path('behaviours/', include('behaviours.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('api.urls')),
    path('points/', include('points.urls')),

]