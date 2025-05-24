#!/usr/bin/env python3
import sys, time, os
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver

def test_serial_options():
    # Try different serial port options
    serial_port = '/dev/ttyACM0'
    
    print("Setting permissions...")
    os.system(f"chmod 666 /{serial_port}")
    
    # Try opening with different settings
    try:
        print("Opening with default settings...")
        driver = BLEDriver(serial_port=serial_port, baud_rate=1000000)
        driver.open()
        print("Default settings worked")
        
        # Try sending a raw command if possible
        adapter = driver.adapter
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        # Try to directly access underlying serial connection if available
        if hasattr(driver, '_serial'):
            print("Serial port attributes:", driver._serial.__dict__)
        
        driver.close()
    except Exception as e:
        print(f"Error with default settings: {e}")

if __name__ == "__main__":
    test_serial_options()
