from django.db import models

class DetectionLog(models.Model):
    # 감지된 객체 이름 (예: person, fire)
    label = models.CharField(max_length=50)
    
    # 정확도 (예: 0.85)
    confidence = models.FloatField()
    
    # 업로드된 이미지 파일 (media/uploads/ 폴더에 날짜별 저장)
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    
    # 생성 시간 (자동 저장)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} ({self.confidence}) - {self.created_at}"