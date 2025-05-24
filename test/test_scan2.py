#!/usr/bin/env python3
import sys, os, time
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver
from pc_ble_driver_py.observers import BLEAdapterObserver

class RawScanner(BLEAdapterObserver):
    def __init__(self):
        super(RawScanner, self).__init__()
        self.count = 0
        
    # Override ALL possible callback methods to see ANY activity
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        self.count += 1
        print(f"RAW ADV PACKET #{self.count}: addr={addr.addr}, rssi={rssi}")
    
    def on_gap_evt_connected(self, adapter, conn_handle, peer_addr, role, conn_params):
        print(f"CONNECT EVENT: {peer_addr.addr}")
    
    def on_gap_evt_disconnected(self, adapter, conn_handle, reason):
        print(f"DISCONNECT EVENT: handle={conn_handle}, reason={reason}")
    
    def on_gap_evt_scan_req_report(self, adapter, conn_handle, peer_addr):
        print(f"SCAN REQUEST: {peer_addr.addr}")
    
    # Add all other possible events
    def __getattr__(self, name):
        # This catches any other event methods that might exist
        if name.startswith('on_'):
            def method(*args, **kwargs):
                print(f"EVENT {name}: called")
            return method
        raise AttributeError(f"{self.__class__.__name__} has no attribute {name}")

def main():
    print("RAW BLE SCANNER - DEBUG MODE")
    
    # Try with the first available serial port
    serial_port = '/dev/ttyACM0'
    
    try:
        print(f"Opening {serial_port}...")
        driver = BLEDriver(serial_port=serial_port, baud_rate=1000000)
        driver.open()
        print("Driver opened!")
        
        adapter = driver.adapter
        scanner = RawScanner()
        adapter.observer_register(scanner)
        
        # Initialize BLE stack
        print("Initializing driver...")
        adapter.driver_init()
        print("Initializing physical layer...")
        adapter.physical_layer_initialize()
        
        # Try several scanning approaches
        for approach_num, scan_config in enumerate([
            # 1. Most aggressive scan
            {'active': True, 'interval_ms': 10, 'window_ms': 10, 'timeout_s': 10},
            # 2. Moderate scan 
            {'active': True, 'interval_ms': 100, 'window_ms': 50, 'timeout_s': 10},
            # 3. Passive scan (doesn't request scan responses)
            {'active': False, 'interval_ms': 100, 'window_ms': 50, 'timeout_s': 10},
        ]):
            print(f"\nTrying scan approach #{approach_num+1}: {scan_config}")
            adapter.gap_scan_start(**scan_config)
            
            # Wait for the scan timeout
            for i in range(scan_config['timeout_s']):
                print(f"Scanning... {i+1}/{scan_config['timeout_s']}s", end="\r")
                time.sleep(1)
            
            print("\nStopping scan...")
            adapter.gap_scan_stop()
            print(f"Approach #{approach_num+1} complete. Packets received: {scanner.count}")
            
            # Reset counter for next approach
            scanner.count = 0
        
        print("\nAll scan approaches completed.")
        driver.close()
        print("Driver closed")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
