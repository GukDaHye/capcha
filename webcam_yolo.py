

from django.http import JsonResponse
import cv2
from ultralytics import YOLO

def detect_objects(request):
    # Load YOLO model
    model = YOLO("yolo11n.pt")

    # Open webcam and capture a single frame
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return JsonResponse({"error": "Failed to capture frame from webcam"}, status=500)

    # Run YOLO on the frame
    results = model.predict(frame, imgsz=640, conf=0.5)

    # Prepare detection results
    detections = []
    for box in results[0].boxes:
        detections.append({
            "class": box.cls.item(),
            "confidence": box.conf.item(),
            "bbox": box.xyxy.tolist()
        })

    return JsonResponse({"detections": detections})

