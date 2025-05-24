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

class ScanObserver(BLEAdapterObserver):
    def __init__(self, adapter):
        super(ScanObserver, self).__init__()
        self.adapter = adapter
        self.devices = {}
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        """Called when an advertisement packet is received"""
        addr_str = addr.addr.upper()
        logger.debug(f"Adv report: addr={addr_str}, rssi={rssi}, type={adv_type}")
        
        if addr_str not in self.devices:
            self.devices[addr_str] = {
                'addr': addr_str,
                'addr_type': addr.addr_type,
                'rssi': rssi,
                'name': adv_data.name if adv_data.name else "Unknown",
                'first_seen': time.time()
            }
            
            # Print device information
            print(f"\nDevice found: {addr_str}")
            print(f"  RSSI: {rssi} dBm")
            print(f"  Name: {adv_data.name if adv_data.name else 'Unknown'}")
            try:
                if hasattr(adv_data, 'service_uuids') and adv_data.service_uuids:
                    print(f"  Services: {', '.join(adv_data.service_uuids)}")
                if hasattr(adv_data, 'manufacturer_data') and adv_data.manufacturer_data:
                    print(f"  Mfr Data: {adv_data.manufacturer_data.hex()}")
            except Exception as e:
                logger.error(f"Error processing adv data: {e}")
        else:
            # Update existing device
            self.devices[addr_str]['rssi'] = rssi
            self.devices[addr_str]['last_seen'] = time.time()
            # Update name if it was unknown before
            if self.devices[addr_str]['name'] == "Unknown" and adv_data.name:
                self.devices[addr_str]['name'] = adv_data.name
                print(f"Updated name for {addr_str}: {adv_data.name}")

def main(serial_port='/dev/ttyACM0', scan_duration=60):
    """Run a BLE scan with the specified parameters"""
    logger.info(f"Starting BLE scan on {serial_port}")
    
    # Initialize the BLE driver
    try:
        driver = BLEDriver(serial_port=serial_port, baud_rate=1000000)
        adapter = driver.adapter
        
        # Create and register observer
        scanner = ScanObserver(adapter)
        adapter.observer_register(scanner)
        
        # Open the driver
        driver.open()
        logger.info("Driver opened successfully")
        
        # Initialize BLE stack
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        # Wide scanning parameters (more aggressive)
        scan_params = {
            'active': True,       # Request scan responses
            'interval_ms': 60,    # Shorter interval (was 100)
            'window_ms': 40,      # Wider window (was 50)
            'timeout_s': 0        # Continuous scan
        }
        
        logger.info(f"Starting scan with params: {scan_params}")
        adapter.gap_scan_start(**scan_params)
        
        # Run for the specified duration
        start_time = time.time()
        try:
            while time.time() - start_time < scan_duration:
                remaining = int(scan_duration - (time.time() - start_time))
                if remaining % 5 == 0:
                    devices_count = len(scanner.devices)
                    print(f"\rScanning... {remaining}s left, {devices_count} devices found", end="")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nScan interrupted by user")
        
        # Stop scan
        adapter.gap_scan_stop()
        logger.info("Scan stopped")
        
        # Print summary
        print("\n\n=== SCAN RESULTS ===")
        if len(scanner.devices) == 0:
            print("No devices found!")
        else:
            print(f"Found {len(scanner.devices)} devices:")
            for i, (addr, device) in enumerate(sorted(scanner.devices.items(), 
                                               key=lambda x: x[1]['rssi'], reverse=True)):
                print(f"{i+1}. {device['name']} ({addr})")
                print(f"   RSSI: {device['rssi']} dBm")
        
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure driver is closed
        try:
            driver.close()
            logger.info("Driver closed")
        except:
            pass

if __name__ == "__main__":
    # Get serial port from command line
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    main(port, duration)
