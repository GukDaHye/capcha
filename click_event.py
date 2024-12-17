import os
import cv2

# 이미지 경로 설정
image_path = os.path.abspath("media/yolo_list/bus001.jpeg")
print(f"Image path: {image_path}")

# 이미지 존재 여부 확인
if not os.path.exists(image_path):
    print("Error: Image file not found at the specified path.")
else:
    print("Image file found!")

# 이미지 불러오기
img = cv2.imread(image_path)
if img is None:
    print("Failed to load image. Check file permissions or format.")
else:
    print("Click on the image to get coordinates.")

    # 마우스 이벤트 콜백 함수
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 좌클릭 이벤트
            print(f"Clicked coordinates: ({x}, {y})")  # 클릭한 좌표 출력
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, f"({x}, {y})", (x, y), font, 0.5, (0, 255, 0), 2)  # 좌표 표시
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)  # 클릭 위치에 빨간 점 표시
            cv2.imshow('Image', img)

    # 이미지 표시 및 좌표 추출
    cv2.imshow('Image', img)
    cv2.setMouseCallback('Image', click_event)  # 마우스 콜백 함수 설정
    cv2.waitKey(0)
    cv2.destroyAllWindows()
