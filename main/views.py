import base64
import os
import time

import serial
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from capcha import settings
from main.webcam_yolo import detect_objects
from .detect_person import detect_objects_person_all_frame, detect_objects_person_ver2, detect_objects_person_ver3
from .models import CongestionData, BusStop


class IndexView(TemplateView):
    template_name = 'main/index.html'  # 템플릿 경로 지정

    def get_context_data(self, **kwargs):
        # 템플릿에 전달할 데이터 정의
        context = super().get_context_data(**kwargs)
        context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        return context


class DashboardView(TemplateView):
    template_name = 'main/dashboard.html'

    CONGESTION_MAP = {
        "Empty": "여유",
        "Moderate": "보통",
        "High": "혼잡"
    }
    # 영어에서 한글로 변환
    congestion_level = CongestionData.objects.latest('timestamp').congestion_level

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        congestion_level = CongestionData.objects.latest('timestamp').congestion_level
        translated_congestion = self.CONGESTION_MAP.get(congestion_level, "Empty")
        context['congestion_data'] = translated_congestion  # 한글 변환된 값 전달

        return context


class DashboardMapView(TemplateView):
    template_name = 'main/dashboard_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        # 최근 1개 congestion_level만 가져오기
        return context


class ObjectDetectionView(View):
    template_name = 'main/detection.html'

    def send_char(self, ser, value):
        """
        Send a single character via UART.
        """
        if isinstance(value, str) and len(value) == 1:
            ser.write(value.encode())  # Convert to bytes and send
            print(f"Sent: '{value}' (ASCII: {ord(value)})")
        else:
            print(f"Error: '{value}' is not a valid character.")

    def send_human(self, ser):
        """
        Send the string "human" via UART.
        """
        word = "human"
        for char in word:
            self.send_char(ser, char)
            time.sleep(0.5)  # Add delay for UART transmission
        print("Sent: 'human'")

    # def determine_congestion(self, person_locations, rois):
    #     """
    #     Determine congestion level based on person locations and ROIs.
    #     """
    #     detected = {
    #         'empty': False,
    #         'moderate': False,
    #         'high': False
    #     }
    # 
    #     for location in person_locations:
    #         for roi_name, roi_coords in rois.items():
    #             if location in roi_coords:
    #                 detected[roi_name] = True
    # 
    #     # Determine congestion level
    #     if detected['high'] or (detected['moderate'] and detected['empty']):
    #         return 'High'
    #     elif detected['moderate']:
    #         return 'Moderate'
    #     else:
    #         return 'Empty'

    def save_image(self, img_base64, stop_name):
        """
        Save base64 image to media directory.
        """
        import base64, os, time
        from django.conf import settings

        # Decode the image
        img_data = base64.b64decode(img_base64)

        # Define the file path
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{stop_name}_{timestamp}.jpg"
        filepath = os.path.join(settings.MEDIA_ROOT, 'congestion_images', stop_name, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Ensure directory exists

        # Write the image to disk
        with open(filepath, 'wb') as f:
            f.write(img_data)

        # Return relative path for storing in the database
        return os.path.relpath(filepath, settings.MEDIA_ROOT)

    def get(self, request, *args, **kwargs):
        #     YOLO 감지 수행 (웹캠 사용)
        #     result = detect_objects()

        # 1. 웹캠 사용
        # result= detect_objects_person_all_frame(request)
        # print(result)

        # 2. 이미지 파일 사용
        # image_path = os.path.join(settings.BASE_DIR, "media/yolo_list/bus001.jpeg")
        # result = detect_objects_person_ver2(request, image_path=image_path)
        # print(result)

        # Use YOLO to detect objects (e.g., from an image file or webcam)
        image_path = os.path.join(settings.BASE_DIR, "media/yolo_list/bus001.jpeg")
        result = detect_objects_person_ver2(request, image_path=image_path)
        # result = detect_objects_person_ver2(request)

        # Handle errors
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=500)

        # Count persons detected
        # person_count = sum(1 for det in result["detections"] if det["class"] == 0)
        person_count = result["person_count"]
        print(f"Detected {person_count} persons.")

        # Extract person detections
        # person_locations = [det["bbox"] for det in result["detections"] if det["class"] == 0]
        # print(f"Person locations: {person_locations}")
        #
        # # Determine congestion level
        # congestion_level = self.determine_congestion(person_locations, rois)
        # print(f"Congestion level: {congestion_level}")

        # Save congestion data
        try:
            bus_stop = BusStop.objects.get(stop_id=1)

            # Save image
            image_path = self.save_image(result["image_data"], bus_stop.name)
            congestion_level = result["overall_congestion"]

            # Save to database
            congestion_data = CongestionData.objects.create(
                stop=bus_stop,
                # student_count=len(person_locations),
                student_count=person_count,
                congestion_level=congestion_level,
                image=image_path
            )
            print(f"Saved congestion data: {congestion_data}  result: {result['congestion_levels']}")

        except BusStop.DoesNotExist:
            print("Bus stop with ID 1 does not exist.")
            return JsonResponse({"error": "Bus stop not found"}, status=500)

        # UART Transmission
        try:
            ser = serial.Serial(
                port='/dev/serial0',
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )

            # if congestion_level == 'High':
            #     self.send_char(ser, 'H')  # High congestion
            # elif congestion_level == 'Moderate':
            #     self.send_char(ser, 'M')  # Moderate congestion
            # elif congestion_level == 'Empty':
            #     self.send_char(ser, 'E')  # Empty congestion

            if person_count > 0:
                print("Sending 'human' via UART...")
                for _ in range(person_count+8):
                    self.send_human(ser)
                    print(f'person_count: {_+1}')

            else:
                print("No humans detected. Nothing to send via UART.")

            self.send_char(ser, '@')  # End transmission


        except serial.SerialException as e:
            print(f"Serial error: {e}")

        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()

        # Render the template with detection results
        context = {
            "image_data": result["image_data"],
            "detections": result["detections"],

        }
        return render(request, self.template_name, context)
