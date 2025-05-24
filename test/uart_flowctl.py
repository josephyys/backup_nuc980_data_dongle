#!/usr/bin/env python3
import sys
sys.path.append('/data/usr/lib/python3/site-packages')
from pc_ble_driver_py import BLEDriver

# Try different flow control settings
for flow_control in [True, False]:
    print(f"\nTesting with flow_control={flow_control}")
    try:
        driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000, 
                           auto_flash=False, flow_control=flow_control)
        driver.open()
        print("  Driver opened successfully")
        version = driver.ble_version_get()
        print(f"  Version: {version}")
        driver.close()
    except Exception as e:
        print(f"  Error: {e}")
