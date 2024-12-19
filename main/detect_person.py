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


def detect_objects_person_all_frame(request, image_path=None):
    # YOLO 모델 로드
    model = YOLO("../yolov8s.pt")  # YOLO 모델 경로 확인

    # 이미지 소스 선택
    if image_path:
        # 이미지 파일 읽기
        frame = cv2.imread(image_path)
        if frame is None:
            return {"error": "Failed to read image. Check the image path."}
    else:
        # 웹캠 초기화
        usb_camera_index = 0  # USB 카메라 기본 인덱스
        default_camera_index = 0  # 내장 카메라 기본 인덱스

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

    # ROI 다각형 좌표 설정 (순서 맞춤) (전체 펜스 영역)
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
    # cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 255), thickness=3)  # 노란색 다각형 표시

    # ROI 외부를 마스킹한 이미지 생성
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)  # 다각형 내부를 채움
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

    # YOLO 객체 감지 (사람만)
    results = model.predict(masked_frame, imgsz=1280, conf=0.5)

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

def detect_objects_person_ver3(request, image_path=None):
    # YOLO 모델 로드
    model = YOLO("../yolov8n.pt")

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

    # ROI 설정 (여유, 보통, 혼잡)
    rois = {
        'empty': np.array([(213, 324), (814, 250), (877, 476), (988, 651), (702, 889), (278, 797)], dtype=np.int32),
        'moderate': np.array([(814, 250), (1028, 223), (1134, 390), (1171, 483), (1119, 553), (988, 651), (877, 476)],
                             dtype=np.int32),
        'high': np.array([(1028, 223), (1306, 234), (1366, 253), (1352, 366), (1247, 415), (1171, 483), (1023, 399)],
                         dtype=np.int32)
    }

    # ROI 영역 시각적으로 표시
    for key, points in rois.items():
        color = (135, 206, 235) if key == 'empty' else (0, 255, 255) if key == 'moderate' else (0, 0, 255)
        cv2.polylines(frame, [points], isClosed=True, color=color, thickness=2)

    # YOLO 객체 감지 (사람만)
    results = model.predict(frame, imgsz=640, conf=0.5, classes=0)

    # 각 구역별 사람 수 계산
    region_counts = {key: 0 for key in rois.keys()}
    detections = []
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        center_x = int((bbox[0] + bbox[2]) / 2)
        center_y = int((bbox[1] + bbox[3]) / 2)
        confidence = round(float(box.conf.item()), 2)
        class_id = int(box.cls.item())

        # 중심점이 각 ROI 내부에 있는지 확인
        roi_matched = False
        for key, points in rois.items():
            if cv2.pointPolygonTest(points, (center_x, center_y), False) >= 0:
                region_counts[key] += 1
                roi_matched = True
                break  # 한 ROI에만 포함되도록 처리

        # ROI 내부에 포함된 경우만 바운딩 박스 그리기
        if roi_matched:
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            cv2.putText(frame, f"{confidence:.2f}", (int(bbox[0]), int(bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 1)

        # 모든 객체 감지 정보를 detections에 추가
        detections.append({
            "class": class_id,
            "confidence": confidence,
            "bbox": [round(float(coord), 2) for coord in bbox]
        })

    # 혼잡도 계산 (규칙 기반)
    if region_counts['high'] > 0:
        overall_congestion = "혼잡"
    elif region_counts['moderate'] > 0:
        if region_counts['empty'] > 0:
            overall_congestion = "보통"
        else:
            overall_congestion = "혼잡"
    elif region_counts['empty'] > 0:
        overall_congestion = "여유"
    else:
        overall_congestion = "여유"  # 사람이 없으면 여유로 간주

    # 구역별 혼잡도 계산
    congestion_levels = {}
    for key, count in region_counts.items():
        if count < 1:
            congestion_levels[key] = "Low"
        elif count < 2:
            congestion_levels[key] = "Medium"
        else:
            congestion_levels[key] = "High"

    # 결과 이미지 인코딩
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # 결과 반환
    return {
        "region_counts": region_counts,
        "congestion_levels": congestion_levels,  # 구역별 혼잡도 추가
        "detections": detections,
        "overall_congestion": overall_congestion,
        "image_data": img_base64
    }


def scale_rois(rois, input_width, input_height, ref_width=1920, ref_height=1080):
    """
    기준 해상도를 바탕으로 입력 이미지 해상도에 맞게 ROI 좌표를 조정.

    Args:
        rois (dict): ROI 좌표 사전. 예: {'key': np.array([[x1, y1], [x2, y2], ...])}
        input_width (int): 입력 이미지의 너비.
        input_height (int): 입력 이미지의 높이.
        ref_width (int): 기준 해상도의 너비. 기본값 1920.
        ref_height (int): 기준 해상도의 높이. 기본값 1080.

    Returns:
        dict: 스케일링된 ROI 좌표.
    """
    scale_x = input_width / ref_width
    scale_y = input_height / ref_height

    scaled_rois = {
        key: np.array([(int(x * scale_x), int(y * scale_y)) for x, y in points], dtype=np.int32)
        for key, points in rois.items()
    }
    return scaled_rois


def detect_objects_person_ver2(request, image_path=None):
    # YOLO 모델 로드
    model = YOLO("../yolov8n.pt")

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

    # 입력 이미지 해상도 확인
    input_height, input_width = frame.shape[:2]

    # 기준 ROI (기준 해상도 1600x901에서 작성된 좌표)
    ref_width, ref_height = 1600, 901
    rois = {
        'empty': np.array([[213, 324], [814, 270], [877, 476], [988, 651], [702, 889], [278, 797]], dtype=np.float32),
        'moderate': np.array([[814, 270], [1028, 223], [1134, 390], [1171, 483], [1119, 553], [988, 651], [877, 476]],
                             dtype=np.float32),
        'high': np.array([[1028, 223], [1306, 234], [1366, 253], [1352, 366], [1247, 415], [1171, 483], [1023, 399]],
                         dtype=np.float32)
    }

    # ROI 좌표 비율 기반 스케일링
    scaled_rois = scale_rois(rois, input_width, input_height, ref_width, ref_height)

    # ROI 영역 시각적으로 표시
    for key, points in scaled_rois.items():
        color = (135, 206, 235) if key == 'empty' else (0, 255, 255) if key == 'moderate' else (0, 0, 255)
        cv2.polylines(frame, [points], isClosed=True, color=color, thickness=2)

    # YOLO 객체 감지 (사람만)
    results = model.predict(frame, imgsz=640, conf=0.5, classes=0)
    person_count = len(results[0].boxes)
    print(f"Detected {len(results[0].boxes)} persons.")

    # 각 구역별 사람 수 계산
    region_counts = {key: 0 for key in scaled_rois.keys()}
    detections = []
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
    center_x = int((bbox[0] + bbox[2]) / 2)
    center_y = int((bbox[1] + bbox[3]) / 2)
    confidence = round(float(box.conf.item()), 2)
    class_id = int(box.cls.item())  # 클래스 ID 가져오기

    # 중심점이 각 ROI 내부에 있는지 확인
    roi_matched = False
    for key, points in scaled_rois.items():
        if cv2.pointPolygonTest(points, (center_x, center_y), False) >= 0:
            region_counts[key] += 1
            roi_matched = True
            break  # 첫 번째 ROI에만 포함되도록 처리

    # ROI 내부에 포함된 경우 바운딩 박스 그리기
    if roi_matched:
        cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
        cv2.putText(frame, f"{confidence:.2f}", (int(bbox[0]), int(bbox[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # 감지 정보 추가 (class 포함)
    detections.append({
        "class": class_id,  # 클래스 추가
        "confidence": confidence,
        "bbox": [round(float(coord), 2) for coord in bbox]
    })


    # 구역별 혼잡도 계산
    congestion_levels = {}
    for key, count in region_counts.items():
        if count < 1:
            congestion_levels[key] = "Low"
        elif count < 2:
            congestion_levels[key] = "Medium"
        else:
            congestion_levels[key] = "High"

    # 전체 혼잡도 계산 (규칙 기반)
    if region_counts['high'] > 0:
        overall_congestion = "혼잡"
    elif region_counts['moderate'] > 0:
        if region_counts['empty'] > 0:
            overall_congestion = "보통"
        else:
            overall_congestion = "혼잡"
    elif region_counts['empty'] > 0:
        overall_congestion = "여유"
    else:
        overall_congestion = "여유"  # 사람이 없으면 여유로 간주

    # 결과 이미지 인코딩
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # 결과 반환
    return {
        "region_counts": region_counts,
        "congestion_levels": congestion_levels,  # 구역별 혼잡도 반환
        "overall_congestion": overall_congestion,  # 전체 혼잡도 반환
        "detections": detections,
        "image_data": img_base64,
        "person_count": person_count
    }
