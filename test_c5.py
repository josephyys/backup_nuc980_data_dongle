#!/usr/bin/env python3
import time
from simple_nordic_wrapper_v5 import BLEDriver

# Create driver with your dongle's serial port
driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
driver.open()

try:
    driver.scan()
    # Scan for 30 seconds
    for i in range(30):
        time.sleep(1)
        print(f"Scanning... {i+1}/30s")
except KeyboardInterrupt:
    print("\nScan interrupted")
finally:
    driver.close()
    print("\nComplete.")

