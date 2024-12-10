from django.http import JsonResponse, HttpResponse
import cv2
from ultralytics import YOLO
import base64
import time

def detect_objects(request):
    # Load YOLO model
    model = YOLO("yolo11n.pt")  # Ensure the model file is available in your working directory

    # Open webcam
    cap = cv2.VideoCapture(0)  # 0: default camera index
    if not cap.isOpened():
        return JsonResponse({"error": "Webcam not accessible. Check if it's connected properly."}, status=500)

    # Camera initialization delay
    time.sleep(2)  # Allow the camera to initialize

    # Capture a single frame
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return JsonResponse({"error": "Failed to capture frame from webcam"}, status=500)

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
        detections.append({
            "class": box.cls.item(),
            "confidence": box.conf.item(),
            "bbox": box.xyxy.tolist()
        })

    # Return HTML response with image and detection results
    html = f"""
    <html>
    <body>
        <h1>YOLO Detection Results</h1>
        <img src="data:image/jpeg;base64,{img_base64}" alt="Captured Frame" style="max-width: 100%; height: auto;"/>
        <pre>{detections}</pre>
    </body>
    </html>
    """
    return HttpResponse(html)