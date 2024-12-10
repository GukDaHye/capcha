from ultralytics import YOLO
import cv2

# Load the YOLO model (Ensure the correct model file is available in your working directory)
model = YOLO("yolo11n.pt")  # Replace with your desired YOLO model file

# Open the default webcam (0 is the default camera index)
cap = cv2.VideoCapture(0)

# Set webcam resolution (optional, depends on your webcam capabilities)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Start the webcam feed
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from webcam.")
        break

    # Run the YOLO model on the captured frame
    results = model.predict(frame, imgsz=640, conf=0.5)  # Adjust `conf` for confidence threshold

    # Visualize detections on the frame
    annotated_frame = results[0].plot()

    # Display the frame with detections
    cv2.imshow("YOLO Webcam Detection", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()

