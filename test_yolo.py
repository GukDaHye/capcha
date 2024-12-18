import os

from ultralytics import YOLO
import cv2
import numpy as np

from capcha import settings


# 혼잡도 평가 함수
def evaluate_congestion(detections, rois):
    congestion_levels = {'empty': 0, 'moderate': 0, 'high': 0}
    for detection in detections:
        x, y = detection[:2]  # 탐지된 객체 중심 좌표
        for level, roi in rois.items():
            if cv2.pointPolygonTest(np.array(roi, np.int32), (x, y), False) >= 0:
                congestion_levels[level] += 1
                break
    return congestion_levels

# 메인 실행
if __name__ == "__main__":
    # YOLOv8 모델 로드
    model = YOLO("../yolov8n.pt")  # yolov8n.pt 경로

    # 이미지 읽기
    image_path =  os.path.join(settings.BASE_DIR, "media/yolo_list/bus001.jpeg")
    image = cv2.imread(image_path)

    # 탐지 실행
    results = model(image)  # YOLOv8 모델로 탐지
    detections = []
    for result in results:
        for box in result.boxes.xywh.cpu().numpy():  # 탐지된 박스 좌표 (x, y, w, h)
            detections.append((int(box[0]), int(box[1])))  # 중심 좌표 저장

    # ROI 설정 (여유, 보통, 혼잡)
    rois = {
        'empty': [(213, 324), (814, 270), (877, 476), (988, 651), (702, 889), (278, 797)],
        'moderate': [(814, 270), (1028, 223), (1134, 390), (1171, 483), (1119, 553), (988, 651),(877, 476)],
        'high': [(1028, 223), (1306, 234), (1366, 253), (1352, 366), (1247, 415), (1171, 483), (1023, 399)]
    }

    # 혼잡도 평가
    congestion = evaluate_congestion(detections, rois)

    # 결과 출력
    print("Congestion Levels:")
    for level, count in congestion.items():
        print(f"{level.capitalize()}: {count} objects")

    # 시각화
    for level, roi in rois.items():
        color = (0, 255, 0) if level == 'spacious' else (0, 255, 255) if level == 'moderate' else (0, 0, 255)
        cv2.polylines(image, [np.array(roi, np.int32)], isClosed=True, color=color, thickness=2)

    for detection in detections:
        x, y = detection
        cv2.circle(image, (x, y), radius=5, color=(255, 0, 0), thickness=-1)

    # 결과 출력
    cv2.imshow("Congestion Detection", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
