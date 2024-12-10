

from django.http import JsonResponse
import cv2
from ultralytics import YOLO

from django.http import JsonResponse
import cv2
from ultralytics import YOLO

def detect_objects(request):
    # Load YOLO model
    model = YOLO("yolo11n.pt")

    # Open webcam
    # 0: Default webcam (usually the laptop's or Pi's camera)
    # Adjust the index if multiple cameras are connected
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return JsonResponse({"error": "Webcam not accessible. Check if it's connected properly."}, status=500)

    # Capture a single frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return JsonResponse({"error": "Failed to capture frame from webcam"}, status=500)

    # Run YOLO on the captured frame
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
