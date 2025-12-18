import cv2
import torch
import requests
import time
import datetime
from io import BytesIO
import warnings

# [설정] 경고 메시지 무시 (터미널 깔끔하게 하기 위해)
warnings.filterwarnings("ignore")

# ================= 설정 구간 =================
# 1. Django 서버 주소 (https인지 http인지, 주소 끝에 / 있는지 확인)
# SERVER_URL = "http://byeongmin.pythonanywhere.com/api/detect/"
SERVER_URL = 'http://0.0.0.0:8000/api/detect/'

# 2. 감지할 객체 번호 (0: person)
TARGET_CLASSES = [0] 

# 3. 전송 쿨다운 (초) - 보고서용으로 60초 설정
SEND_COOLDOWN = 60.0 
# ============================================

def main():
    # 1. YOLOv5 모델 로드
    print("Loading YOLOv5 model...")
    # trust_repo=True로 경고 방지
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    last_sent_time = 0 
    print(f"Start Monitoring... Target Classes: {TARGET_CLASSES}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 2. YOLO 추론
        results = model(frame)
        detections = results.xyxy[0].cpu().numpy()
        
        detected = False
        best_conf = 0
        best_label = ""
        
        # 3. 감지된 객체 분석
        for *xyxy, conf, cls in detections:
            if int(cls) in TARGET_CLASSES and conf > 0.5:
                detected = True
                # 가장 정확도가 높은 객체 정보 저장
                if conf > best_conf:
                    best_conf = float(conf)
                    best_label = model.names[int(cls)]

                # 화면에 네모 그리기
                label_text = f"{model.names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                cv2.putText(frame, label_text, (int(xyxy[0]), int(xyxy[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 4. 전송 및 쿨다운 로직 (수정된 부분)
        current_time = time.time()
        
        # [중요] 일단 '무언가 감지되었을 때'만 판단함
        if detected:
            # 쿨다운 시간이 지났으면 -> 전송
            if current_time - last_sent_time > SEND_COOLDOWN:
                print(f"🚀 {best_label}({best_conf:.2f}) 감지됨! 서버로 전송 중...")
                
                # 이미지 인코딩
                _, img_encoded = cv2.imencode('.jpg', frame)
                img_bytes = BytesIO(img_encoded.tobytes())
                
                files = {
                    'image': ('detect.jpg', img_bytes, 'image/jpeg')
                }
                
                data = {
                    'label': best_label,
                    'confidence': str(best_conf),
                    'title': f"Detected {best_label} at {datetime.datetime.now().strftime('%H:%M:%S')}",
                }
                
                try:
                    response = requests.post(SERVER_URL, files=files, data=data)
                    if response.status_code == 200 or response.status_code == 201:
                        print(f"✅ 전송 성공!")
                        last_sent_time = current_time 
                    else:
                        print(f"❌ 전송 실패: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ 연결 에러: {e}")
            
            # 쿨다운 시간이 아직 안 지났으면 -> 대기 메시지 출력 (보고서 캡처용)
            else:
                # 1초에 한 번만 로그 출력 (도배 방지)
                if int(current_time) % 2 == 0: 
                    left_time = int(SEND_COOLDOWN - (current_time - last_sent_time))
                    # [수정] label 변수가 아니라 best_label을 사용해야 에러가 안 남
                    print(f"⏳ {best_label} 감지됐지만 쿨다운 중... ({left_time}초 남음) - 전송 생략")

        # 5. 화면 출력
        cv2.imshow('YOLOv5 Edge Client', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()