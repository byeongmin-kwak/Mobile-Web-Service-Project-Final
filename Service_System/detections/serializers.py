from rest_framework import serializers
from .models import DetectionLog

class DetectionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionLog
        fields = '__all__' # 모든 필드 포함