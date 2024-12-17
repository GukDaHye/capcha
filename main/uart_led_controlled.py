# views.py
import os

import serial
import time
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

# Function to configure the serial connection
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
    ser = None

# Function to send an 8-bit integer via UART
def send_count(value):
    if ser is None:
        raise EnvironmentError("Serial port is not available. Ensure this is running on a Raspberry Pi.")
    if 0 <= value <= 255:
        ser.write(value.to_bytes(1, byteorder='big'))  # Send as a single byte
        print(f"Sent: {value} (Binary: {bin(value)[2:].zfill(8)})")
    else:
        raise ValueError(f"Value {value} is out of range (0-255).")

# Django view to trigger the send_count function
def send_uart_sequence(request):
    try:
        if ser:
            for value in [2, 9, 11]:  # Sequence of numbers to send
                send_count(value)
                time.sleep(1)  # Delay between sending each number
            return JsonResponse({'status': 'success', 'message': 'Sequence sent successfully.'})
        else:
            raise EnvironmentError("Serial connection not initialized.")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})