from django.shortcuts import render


#behaviours默认视图
def index(request):
    return render(request, 'behaviours/index.html')

# 在 behaviours 的 views.py 文件中
from rest_framework import generics
from .models import BehaviorRecord
from .serializers import BehaviorRecordSerializer

class BehaviorRecordListCreateAPIView(generics.ListCreateAPIView):
    queryset = BehaviorRecord.objects.all()
    serializer_class = BehaviorRecordSerializer
