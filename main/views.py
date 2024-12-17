import time

import serial
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from main.webcam_yolo import detect_objects
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        return context

class DashboardMapView(TemplateView):
    template_name = 'main/dashboard_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['congestion_data'] = CongestionData.objects.select_related('stop').order_by('-timestamp')[:10]
        return context


class ObjectDetectionView(View):
    template_name = 'main/detection.html'

    def send_char(self, ser, value):
        """
        Send a single character via UART.
        """
        if isinstance(value, str) and len(value) == 1:  # Ensure it's a single character
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
            self.send_char(ser, char)  # Send each character in the word
            time.sleep(0.05)  # Add a short delay between characters to ensure proper timing
        print("Sent: 'human'")

    def get(self, request, *args, **kwargs):
        # detect_objects 함수를 호출하여 YOLO 감지 수행
        result = detect_objects()

        # 에러가 발생하면 JSON 응답 반환
        if "error" in result:
            return JsonResponse({"error": result["error"]}, status=500)

        # Count the number of "person" class detections (assuming class ID 0 corresponds to "person")
        person_count = sum(1 for det in result["detections"] if det["class"] == 0)
        print(f"Detected {person_count} persons.")

        # Save the detection result to CongestionData
        try:
            # Get the bus stop instance (bus stop ID is hardcoded to 1 for this example)
            bus_stop = BusStop.objects.get(stop_id=1)

            # Determine congestion level based on person count
            if person_count == 0:
                congestion_level = "Empty"
            elif person_count <= bus_stop.capacity // 2:
                congestion_level = "Moderate"
            else:
                congestion_level = "High"

            # Save data to CongestionData model
            congestion_data = CongestionData.objects.create(
                stop=bus_stop,
                student_count=person_count,
                congestion_level=congestion_level
            )
            print(f"Saved congestion data: {congestion_data}")

        except BusStop.DoesNotExist:
            print("Bus stop with ID 1 does not exist.")
            return JsonResponse({"error": "Bus stop not found"}, status=500)

        # UART 전송
        try:
            ser = serial.Serial(
                port='/dev/serial0',  # UART port on Raspberry Pi
                baudrate=9600,       # Baud rate (matches FPGA prescaler)
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )

            if person_count > 0:
                print("Sending 'human' via UART...")
                self.send_human(ser)
            else:
                print("No humans detected. Nothing to send via UART.")

        except serial.SerialException as e:
            print(f"Serial error: {e}")

        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()  # Close the serial connection

        # 템플릿 렌더링
        context = {
            "image_data": result["image_data"],
            "detections": result["detections"],
        }
        return render(request, self.template_name, context)