import serial
import time

# Configure the serial connection
ser = serial.Serial(
    port='/dev/serial0',   # UART port on Raspberry Pi
    baudrate=9600,         # Baud rate (matches FPGA prescaler)
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Function to send a single character via UART
def send_char(value):
    if isinstance(value, str) and len(value) == 1:  # Ensure it's a single character
        ser.write(value.encode())  # Convert to bytes and send
        print(f"Sent: '{value}' (ASCII: {ord(value)})")
    else:
        print(f"Error: '{value}' is not a valid character.")

# Function to send the string "human" via UART
def send_human():
    word = "human"
    for char in word:
        send_char(char)  # Send each character in the word
        time.sleep(0.05)  # Add a short delay between characters to ensure proper timing
    print("Sent: 'human'")

try:
    # Continuously send "human" every second
    while True:
        send_human()
        time.sleep(1)  # Wait 1 second before sending again
except KeyboardInterrupt:
    print("Transmission stopped by user.")
finally:
    ser.close()  # Close the serial connection

