#!/usr/bin/env python3
import sys
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver

def test_connectivity():
    print("Testing Nordic BLE dongle connectivity...")
    
    try:
        # Create driver instance
        driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
        print("Driver object created successfully")
        
        # Open the driver
        driver.open()
        print("Driver opened successfully")
        
        # Get version info
        version = driver.ble_version_get()
        print(f"BLE Version: {version}")
        
        # Get local BLE address if supported
        try:
            address = driver.ble_cfg_get()
            print(f"Local BLE address: {address}")
        except:
            print("Unable to get local BLE address")
            
        # Try setting advertising data (doesn't require scanning)
        try:
            driver.ble_cfg_set(1, 1)  # Example parameters
            print("Successfully executed ble_cfg_set")
        except Exception as e:
            print(f"ble_cfg_set test: {e}")
        
        # Close the driver
        driver.close()
        print("Driver closed successfully")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_connectivity()
