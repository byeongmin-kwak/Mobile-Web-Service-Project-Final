from django.contrib import admin
from .models import DetectionLog

# 관리자 페이지에서 목록을 어떻게 보여줄지 설정
class DetectionLogAdmin(admin.ModelAdmin):
    # 목록에 보여질 컬럼들 (번호, 라벨, 정확도, 찍힌 시간)
    list_display = ('id', 'label', 'confidence', 'created_at')
    
    # 우측에 필터 추가 (라벨별로 모아보기 기능)
    list_filter = ('label',)
    
    # 검색 기능 추가 (라벨이나 날짜로 검색)
    search_fields = ('label', 'created_at')
    
    # 최신순 정렬
    ordering = ('-created_at',)

# 위 설정을 적용해서 모델 등록
admin.site.register(DetectionLog, DetectionLogAdmin)