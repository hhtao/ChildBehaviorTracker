#behaviours/urls.py
from django.urls import path
from .views import GoogleSearchAPIView,BingSearchAPIView,YahooSearchAPIView

urlpatterns = [   
    path('search/', GoogleSearchAPIView.as_view(), name='google-search'),
    path('bingsearch/', BingSearchAPIView.as_view(), name='bing_search'),
    path('yahoosearch/', YahooSearchAPIView.as_view(), name='yahoo_search'),
    #path('behv/', BehaviorRecordListCreateAPIView.as_view(), name='behv'),
]