from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from detections.views import UploadDetectionView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API 주소: http://서버IP:8000/api/detect/
    path('api/detect/', UploadDetectionView.as_view(), name='upload_detection'),
]

# 미디어 파일(이미지) 접근을 위한 URL 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)