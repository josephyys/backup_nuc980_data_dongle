#!/usr/bin/env python3
import serial
import time

def raw_serial_test():
    try:
        # Try to open serial port directly
        ser = serial.Serial('/dev/ttyACM0', 1000000, timeout=1)
        print("Serial port opened directly")
        
        # Send some basic data
        ser.write(b'\x01\x02\x03\x04')
        print("Sent test data")
        
        # Read any response
        response = ser.read(100)
        print(f"Response: {response.hex()}")
        
        ser.close()
        print("Serial port closed")
    except Exception as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    raw_serial_test()
