
#!/usr/bin/env python3
import sys, time
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver
from pc_ble_driver_py.observers import BLEAdapterObserver

class PrintingObserver(BLEAdapterObserver):
    def __init__(self):
        super(PrintingObserver, self).__init__()
        self.devices = {}
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        print(f"\nDEVICE: {addr.addr}, RSSI: {rssi}")
        if hasattr(adv_data, 'name') and adv_data.name:
            print(f"  Name: {adv_data.name}")
        self.devices[addr.addr] = True
        
    # Add debug printing for any other callbacks that might execute
    def __getattr__(self, name):
        if name.startswith('on_'):
            def method(*args, **kwargs):
                print(f"EVENT: {name} called")
            return method
        raise AttributeError(f"No attribute {name}")

def main():
    try:
        driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
        driver.open()
        
        adapter = driver.adapter
        observer = PrintingObserver()
        adapter.observer_register(observer)
        
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        print("Starting scan, please wait...")
        adapter.gap_scan_start(active=True, interval_ms=30, window_ms=20, timeout_s=30)
        
        # Wait for scan to complete or devices to be found
        for i in range(30):
            time.sleep(1)
            print(".", end="", flush=True)
            if len(observer.devices) > 0:
                print(f"\nFound {len(observer.devices)} devices so far")
        
        adapter.gap_scan_stop()
        print("\nScan complete")
        
        if len(observer.devices) == 0:
            print("No devices found")
        else:
            print(f"Found {len(observer.devices)} devices")
        
        driver.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
