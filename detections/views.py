from django.contrib import admin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DetectionLogSerializer
from .models import DetectionLog
import os

class UploadDetectionView(APIView):
    def get(self, request):
        # [표 2-4 구현] 최신 데이터 조회 및 반환
        detections = DetectionLog.objects.all().order_by('-created_at')
        serializer = DetectionLogSerializer(detections, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        # [표 2-3 구현] 데이터 저장
        serializer = DetectionLogSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save() 
            
            # ==========================================
            MAX_COUNT = 100  # 유지할 최대 개수
            current_count = DetectionLog.objects.count()
            
            if current_count > MAX_COUNT:
                delete_count = current_count - MAX_COUNT
                # 가장 오래된 데이터 찾기 (created_at 오름차순)
                old_logs = DetectionLog.objects.order_by('created_at')[:delete_count]
                
                for log in old_logs:
                    # 1. 실제 이미지 파일 삭제 (서버 용량 확보)
                    if log.image:
                        if os.path.isfile(log.image.path):
                            os.remove(log.image.path)
                    # 2. DB 데이터 삭제
                    log.delete()
            # ==========================================
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("에러 발생:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)