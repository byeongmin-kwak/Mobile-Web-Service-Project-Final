import cv2
import torch
import requests
import time
import datetime
from io import BytesIO

# ================= 설정 구간 =================
# 1. Django 서버 주소 (본인 환경에 맞게 수정)
# 예: "http://192.168.0.15:8000/api/detect/"
SERVER_URL = "http://byeongmin.pythonanywhere.com/api/detect/"

# 2. 감지할 객체 번호 (COCO 데이터셋 기준)
# 0: person, 1: bicycle, 2: car ... (필요한 것만 리스트에 추가)
TARGET_CLASSES = [0] 

# 3. 전송 쿨다운 (초) - 너무 자주 보내지 않게 방지
SEND_COOLDOWN = 69.0 
# ============================================

def main():
    # 1. YOLOv5 모델 로드 (trust_repo=True 추가로 경고 해결)
    print("Loading YOLOv5 model...")
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

        # 3. YOLO 추론
        results = model(frame)
        detections = results.xyxy[0].cpu().numpy()
        
        detected = False
        best_conf = 0
        best_label = ""
        
        # 감지된 객체들 확인
        for *xyxy, conf, cls in detections:
            if int(cls) in TARGET_CLASSES and conf > 0.5:
                detected = True
                # 가장 정확도가 높은 객체 정보 저장
                if conf > best_conf:
                    best_conf = float(conf)
                    best_label = model.names[int(cls)]

                # 화면에 그리기
                label_text = f"{model.names[int(cls)]} {conf:.2f}"
                cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)
                cv2.putText(frame, label_text, (int(xyxy[0]), int(xyxy[1])-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 4. 전송 로직
        current_time = time.time()
        if detected and (current_time - last_sent_time > SEND_COOLDOWN):
            print(f"🚀 {best_label}({best_conf:.2f}) 감지됨! 서버로 전송 중...")
            
            # 이미지 인코딩
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = BytesIO(img_encoded.tobytes())
            
            # 파일 데이터
            files = {
                'image': ('detect.jpg', img_bytes, 'image/jpeg')
            }
            
            # [중요] 서버가 요구하는 필수 데이터(label, confidence) 추가
            data = {
                'label': best_label,
                'confidence': str(best_conf),  # 문자열로 변환해서 전송
                'title': f"Detected {best_label} at {datetime.datetime.now().strftime('%H:%M:%S')}",
                'secret_key': "my_secret_password_1234" # (서버 설정에 따라 필요할 수 있음)
            }
            
            try:
                response = requests.post(SERVER_URL, files=files, data=data)
                if response.status_code == 200 or response.status_code == 201:
                    print(f"✅ 전송 성공!")
                    last_sent_time = current_time 
                else:
                    print(f"❌ 전송 실패: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"⚠️ 연결 에러: {e}")

        cv2.imshow('YOLOv5 Edge Client', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()