# 在 behaviours 的 serializers.py 
from rest_framework import serializers
from .models import BehaviorRecord, BehaviorAction, CustomUser

class BehaviorActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BehaviorAction
        fields = ['id', 'description', 'points']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username']

class BehaviorRecordSerializer(serializers.ModelSerializer):
    action = serializers.PrimaryKeyRelatedField(queryset=BehaviorAction.objects.all())
    performer = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    recorder = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = BehaviorRecord
        fields = ['id', 'performance', 'points', 'date', 'action', 'performer', 'recorder']

    def create(self, validated_data):
        validated_data['points'] = validated_data['action'].points
        return super().create(validated_data)
