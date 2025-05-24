#!/usr/bin/env python3

import sys
import os

# Add path if needed
sys.path.append('/data/usr/lib/python3/site-packages')

# Print Python path for diagnosis
print("Python Path:", sys.path)

try:
    import pc_ble_driver_py
    from pc_ble_driver_py import BLEDriver, BLEAdvData, BLEEvtID
    from pc_ble_driver_py.observers import BLEDriverObserver, BLEAdapterObserver
    
    print("Successfully imported pc_ble_driver_py")
    print(f"Version: {pc_ble_driver_py.__version__}")
    
    # Try to detect Nordic USB dongle
    serial_port = '/dev/ttyACM0'  # Adjust if necessary
    
    print(f"Looking for Nordic dongle on {serial_port}")
    
    # Try to initialize the driver
    try:
        driver = BLEDriver(serial_port=serial_port, baud_rate=1000000)
        driver.open()
        print("Successfully opened BLE driver!")
        
        # Get adapter info
        version = driver.ble_version_get()
        print(f"Adapter version: {version}")
        
        # Close the driver propery
        driver.close()
        print("Driver closed successfully")
        
    except Exception as e:
        print(f"Error initializing driver: {str(e)}")
    
except ImportError as e:
    print(f"Failed to import pc_ble_driver_py: {str(e)}")
    
    # Check if library files exist
    if os.path.exists('/data/usr/lib/libnrf-ble-driver-sd_api_v6.so'):
        print("libnrf-ble-driver-sd_api_v6.so exists")
    else:
        print("libnrf-ble-driver-sd_api_v6.so missing!")
        
    # Check for Python module files
    if os.path.exists('/data/usr/lib/python3/site-packages/pc_ble_driver_py'):
        print("pc_ble_driver_py directory exists")
    else:
        print("pc_ble_driver_py directory missing!")
