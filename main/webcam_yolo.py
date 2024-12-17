from django.http import JsonResponse
import cv2
from ultralytics import YOLO
import base64
import time

def detect_objects():
    # Load YOLO model
    model = YOLO("../yolo11n.pt")  # Ensure the model file is available in your working directory

    usb_camera_index = 0  # Commonly, USB cameras are indexed as 0 and 1(external)
    default_camera_index = 1

    # Attempt to open USB camera
    cap = cv2.VideoCapture(usb_camera_index)
    if not cap.isOpened():
        # If USB camera is not accessible, fallback to default camera
        cap = cv2.VideoCapture(default_camera_index)

    if not cap.isOpened():
        return {"error": "No accessible webcam. Check your USB or default camera connection."}

    # Camera initialization delay
    time.sleep(2)  # Allow the camera to initialize

    # Capture a single frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"error": "Failed to capture frame from webcam"}

    # Set frame resolution (optional, depends on webcam capabilities)
    frame = cv2.resize(frame, (640, 480))

    # Run YOLO on the captured frame
    results = model.predict(frame, imgsz=640, conf=0.5)  # Adjust 'conf' for confidence threshold

    # Draw bounding boxes on the frame
    annotated_frame = results[0].plot()

    # Encode the annotated frame to base64 for display in HTML
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # Prepare detection results
    detections = []
    for box in results[0].boxes:
        # Extract bounding box as a flat list and ensure all values are float
        bbox = box.xyxy.tolist()[0]
        detections.append({
            "class": int(box.cls.item()),
            "confidence": round(float(box.conf.item()), 2),
            "bbox": [round(float(coord), 2) for coord in bbox]
        })

    return {
        "image_data": img_base64,
        "detections": detections,
    }