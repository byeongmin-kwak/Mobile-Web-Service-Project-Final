from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import DetectionLogSerializer
from .models import DetectionLog

class UploadDetectionView(APIView):
    def get(self, request):
        # 최신 데이터가 위로 오도록 정렬 (-created_at)
        detections = DetectionLog.objects.all().order_by('-created_at')
        
        # JSON으로 변환
        serializer = DetectionLogSerializer(detections, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        # 안드로이드에서 보낸 데이터와 파일이 request.data에 들어있음
        serializer = DetectionLogSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save() # DB 저장 및 이미지 파일 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print("에러 발생:", serializer.errors) # 디버깅용 로그
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)