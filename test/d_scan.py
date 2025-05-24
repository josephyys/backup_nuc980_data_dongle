#!/usr/bin/env python3

import sys
import time
import logging
sys.path.append('/data/usr/lib/python3/site-packages')

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from pc_ble_driver_py import BLEDriver, BLEAdvData, BLEEvtID
from pc_ble_driver_py.observers import BLEDriverObserver, BLEAdapterObserver

class TestObserver(BLEAdapterObserver):
    def __init__(self):
        super(TestObserver, self).__init__()
        self.device_count = 0
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        self.device_count += 1
        print(f"DEVICE FOUND: {addr.addr}, RSSI: {rssi}")
        if hasattr(adv_data, 'name') and adv_data.name:
            print(f"  Name: {adv_data.name}")

def main():
    try:
        # Create driver and open connection
        driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
        driver.open()
        print("BLE driver opened successfully")
        
        # Get adapter and register observer
        adapter = driver.adapter
        observer = TestObserver()
        adapter.observer_register(observer)
        print("Observer registered")
        
        # Initialize adapter
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        # Start scan
        print("Starting scan for 10 seconds...")
        scan_duration = 10
        adapter.gap_scan_start(active=True, interval_ms=30, window_ms=20, timeout_s=scan_duration)
        
        # THIS IS CRITICAL - Wait for the scan to run
        print(f"Waiting {scan_duration} seconds for scan to complete...")
        for i in range(scan_duration):
            time.sleep(1)
            print(f"Scanning... {i+1}/{scan_duration}s", end="\r")
            
        print("\nScan complete!")
        
        # Stop scan and close connection
        adapter.gap_scan_stop()
        print(f"Found {observer.device_count} devices")
        
        driver.close()
        print("Driver closed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
