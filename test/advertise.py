#!/usr/bin/env python3
import sys, time
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver, BLEAdvData

def test_advertising():
    print("Testing advertising capability...")
    
    try:
        # Create driver instance
        driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
        print("Driver object created")
        
        # Open the driver
        driver.open()
        print("Driver opened successfully")
        
        # Initialize adapter
        adapter = driver.adapter
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        # Create advertising data
        adv_data = BLEAdvData()
        adv_data.name = "NUC980-Test"
        
        # Try to start advertising
        adapter.advertising_data_set(adv_data)
        adapter.advertising_start()
        print("Started advertising as 'NUC980-Test'")
        
        # Advertise for 10 seconds
        time.sleep(10)
        
        # Stop advertising
        adapter.advertising_stop()
        
        # Close driver
        driver.close()
        print("Test completed successfully")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_advertising()
