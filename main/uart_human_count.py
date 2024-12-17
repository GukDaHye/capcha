import os

import serial
import time
import platform
from django.http import JsonResponse

def is_raspberry_pi():
    # First, check if the /proc/device-tree/model file exists
    if os.path.exists('/proc/device-tree/model'):
        try:
            with open('/proc/device-tree/model') as f:
                return 'Raspberry Pi' in f.read()
        except Exception as e:
            print(f"Error reading /proc/device-tree/model: {e}")
            return False

    # Fallback: Check /proc/cpuinfo for Raspberry Pi-specific hardware
    try:
        with open('/proc/cpuinfo') as f:
            cpuinfo = f.read()
        return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
    except Exception as e:
        print(f"Error reading /proc/cpuinfo: {e}")
        return False
# Function to configure serial only on Raspberry Pi
def configure_serial():
    # if not is_raspberry_pi():
    #     raise EnvironmentError("This script is intended to run only on a Raspberry Pi.")
    return serial.Serial(
        port='/dev/serial0',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

# Initialize serial connection
try:
    ser = configure_serial()
except EnvironmentError as e:
    print(f"EnvironmentError: {e}")
    ser = None  # Serial is not configured if not running on Raspberry Pi

# Function to send a single character via UART
def send_char(value):
    if ser is None:
        raise EnvironmentError("Serial port is not available. Ensure this is running on a Raspberry Pi.")
    if isinstance(value, str) and len(value) == 1:  # Ensure it's a single character
        ser.write(value.encode())  # Convert to bytes and send
    else:
        raise ValueError("Invalid character.")

# Function to send the string "human" via UART
def send_human():
    if ser is None:
        raise EnvironmentError("Serial port is not available. Ensure this is running on a Raspberry Pi.")
    word = "human"
    for char in word:
        send_char(char)
        time.sleep(0.05)

# Django view to trigger sending "human"
def send_human_view(request):
    try:
        send_human()
        return JsonResponse({'status': 'success', 'message': 'Message "human" sent successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})