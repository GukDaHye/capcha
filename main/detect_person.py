import os
from django.http import HttpResponse

import cv2
from ultralytics import YOLO
import numpy as np
import base64
import time
from django.conf import settings


def detect_objects_person_see(request):
    # YOLO 모델 로드
    model = YOLO("../yolo11n.pt")  # YOLO 모델 경로 확인

    # 이미지 경로 설정
    image_path = os.path.join(settings.BASE_DIR, "media/yolo_list/bus001.jpeg")
    print(f"Image path: {image_path}")  # 경로 확인용 출력

    # 이미지 읽기
    frame = cv2.imread(image_path)
    if frame is None:
        return HttpResponse("Failed to load image. Check the file path or permissions.", status=500)

    # ROI 다각형 좌표 설정 (순서 맞춤)
    roi_points = np.array([
        [253, 327],  # 좌측 상단
        [756, 274],  # 중앙 상단
        [1026, 258],  # 우측 상단
        [1135, 386],  # 우측 중단
        [1124, 537],  # 우측 하단
        [712, 896],  # 중앙 하단
        [273, 757]  # 좌측 하단
    ], dtype=np.int32)

    # ROI 영역 시각적으로 표시 (다각형)
    cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 255), thickness=3)  # 노란색 다각형 표시

    # ROI 외부를 마스킹한 이미지 생성
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)  # 다각형 내부를 채움
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # YOLO 객체 감지 (사람만)
    results = model.predict(masked_frame, imgsz=640, conf=0.5, classes=0)

    # ROI 내부 사람 수 필터링 및 바운딩 박스 그리기
    person_count = 0
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        class_id = int(box.cls.item())
        confidence = round(float(box.conf.item()), 2)

        # 바운딩 박스 중심점 계산
        center_x = int((bbox[0] + bbox[2]) / 2)
        center_y = int((bbox[1] + bbox[3]) / 2)

        # 중심점이 ROI 다각형 내부에 있는지 확인
        if cv2.pointPolygonTest(roi_points, (center_x, center_y), False) >= 0:
            person_count += 1
            # ROI 내부 객체 바운딩 박스
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # 중심점 표시

    # 감지 결과 출력
    print(f"People detected in polygonal ROI: {person_count}")

    # 이미지 인코딩
    _, buffer = cv2.imencode('.jpg', frame)

    # HttpResponse로 이미지 반환
    return HttpResponse(buffer.tobytes(), content_type="image/jpeg")


def detect_objects_person(request, image_path=None):
    # YOLO 모델 로드
    model = YOLO("../yolo11n.pt")  # YOLO 모델 경로 확인

    # 이미지 소스 선택
    if image_path:
        # 이미지 파일 읽기
        frame = cv2.imread(image_path)
        if frame is None:
            return {"error": "Failed to read image. Check the image path."}
    else:
        # 웹캠 초기화
        usb_camera_index = 0  # USB 카메라 기본 인덱스
        default_camera_index = 1  # 내장 카메라 기본 인덱스

        # USB 카메라 우선 접근
        cap = cv2.VideoCapture(usb_camera_index)
        if not cap.isOpened():
            # USB 카메라 접근 실패 시 내장 카메라로 전환
            cap = cv2.VideoCapture(default_camera_index)

        if not cap.isOpened():
            return {"error": "No accessible webcam. Check your USB or default camera connection."}

        # 카메라 초기화 시간 확보
        time.sleep(2)  # 카메라 초기화 지연

        # 프레임 캡처
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {"error": "Failed to capture frame from webcam"}

    # ROI 다각형 좌표 설정 (순서 맞춤)
    roi_points = np.array([
        [253, 327],  # 좌측 상단
        [756, 274],  # 중앙 상단
        [1026, 258],  # 우측 상단
        [1135, 386],  # 우측 중단
        [1124, 537],  # 우측 하단
        [712, 896],  # 중앙 하단
        [273, 757]   # 좌측 하단
    ], dtype=np.int32)

    # ROI 영역 시각적으로 표시 (다각형)
    cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 255), thickness=3)  # 노란색 다각형 표시

    # ROI 외부를 마스킹한 이미지 생성
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)  # 다각형 내부를 채움
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # YOLO 객체 감지 (사람만)
    results = model.predict(masked_frame, imgsz=640, conf=0.5, classes=0)

    # ROI 내부 사람 수 필터링 및 바운딩 박스 그리기
    person_count = 0
    detections = []
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        class_id = int(box.cls.item())
        confidence = round(float(box.conf.item()), 2)

        # 바운딩 박스 중심점 계산
        center_x = int((bbox[0] + bbox[2]) / 2)
        center_y = int((bbox[1] + bbox[3]) / 2)

        # 중심점이 ROI 다각형 내부에 있는지 확인
        if cv2.pointPolygonTest(roi_points, (center_x, center_y), False) >= 0:
            person_count += 1
            detections.append({
                "class": class_id,
                "confidence": confidence,
                "bbox": [round(float(coord), 2) for coord in bbox]
            })
            # ROI 내부 객체 바운딩 박스
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)  # 중심점 표시

    # 감지 결과 출력
    print(f"People detected in polygonal ROI: {person_count}")

    # 결과 이미지 인코딩
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # 결과 반환
    return {
        "person_count": person_count,
        "image_data": img_base64,
        "detections": detections
    }



# 혼잡도 순서 혼잡 -> 보통 -> 여유 순으로 if문 구분

def detect_objects_person_ver2(request, image_path=None):
    # YOLO 모델 로드
    model = YOLO("../yolo11n.pt")  # YOLO 모델 경로 확인

    # 이미지 소스 선택
    if image_path:
        # 이미지 파일 읽기
        frame = cv2.imread(image_path)
        if frame is None:
            return {"error": "Failed to read image. Check the image path."}
    else:
        # 웹캠 초기화
        usb_camera_index = 0  # USB 카메라 기본 인덱스
        default_camera_index = 1  # 내장 카메라 기본 인덱스

        # USB 카메라 우선 접근
        cap = cv2.VideoCapture(usb_camera_index)
        if not cap.isOpened():
            # USB 카메라 접근 실패 시 내장 카메라로 전환
            cap = cv2.VideoCapture(default_camera_index)

        if not cap.isOpened():
            return {"error": "No accessible webcam. Check your USB or default camera connection."}

        # 카메라 초기화 시간 확보
        time.sleep(2)  # 카메라 초기화 지연

        # 프레임 캡처
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {"error": "Failed to capture frame from webcam"}

    # ROI 다각형 좌표 설정
    roi_points = np.array([
        [253, 495], [210, 276], [813, 224], [1027, 234], [1132, 232],
        [1222, 223], [1289, 233], [1352, 250], [1347, 378], [1246, 424],
        [1185, 473], [1113, 554], [991, 675], [703, 860], [267, 725]
    ], dtype=np.int32)

    # 세부 구간(Sub-ROI) 정의
    sub_rois = [
        np.array([[253, 495], [210, 276], [813, 224], [703, 860]], dtype=np.int32),
        np.array([[813, 224], [1027, 234], [1352, 250], [1246, 424]], dtype=np.int32),
        np.array([[1246, 424], [1185, 473], [991, 675], [703, 860]], dtype=np.int32)
    ]

    # ROI 영역 시각적으로 표시
    cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 255), thickness=3)

    # ROI 외부를 마스킹한 이미지 생성
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # YOLO 객체 감지 (사람만)
    results = model.predict(masked_frame, imgsz=640, conf=0.5, classes=0)

    # 세부 구간별 사람 수 계산
    sub_region_counts = []
    detections = []
    for sub_roi in sub_rois:
        sub_count = 0
        for box in results[0].boxes:
            bbox = box.xyxy.tolist()[0]
            center_x = int((bbox[0] + bbox[2]) / 2)
            center_y = int((bbox[1] + bbox[3]) / 2)
            confidence = round(float(box.conf.item()), 2)
            class_id = int(box.cls.item())

            # 중심점이 Sub-ROI 내부에 있는지 확인
            if cv2.pointPolygonTest(sub_roi, (center_x, center_y), False) >= 0:
                sub_count += 1

            # 모든 객체 감지 정보를 detections에 추가
            detections.append({
                "class": class_id,
                "confidence": confidence,
                "bbox": [round(float(coord), 2) for coord in bbox]
            })

        sub_region_counts.append(sub_count)

    # 각 구간별 혼잡도 계산
    congestion_levels = []
    for count in sub_region_counts:
        if count < 3:
            congestion_levels.append("Low")
        elif count < 7:
            congestion_levels.append("Medium")
        else:
            congestion_levels.append("High")

    # 결과 이미지 인코딩
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # 결과 반환
    return {
        "sub_region_counts": sub_region_counts,
        "congestion_levels": congestion_levels,
        "detections": detections,
        "image_data": img_base64
    }



# 5명 일때
# @
# 8명 + =3 11