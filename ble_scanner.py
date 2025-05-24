#!/usr/bin/env python3

import sys
import time
sys.path.append('/data/usr/lib/python3/site-packages')

from pc_ble_driver_py import BLEDriver, BLEAdvData, BLEEvtID
from pc_ble_driver_py.observers import BLEDriverObserver, BLEAdapterObserver

class BLEScanner(BLEAdapterObserver):
    def __init__(self, adapter):
        super(BLEScanner, self).__init__()
        self.adapter = adapter
        self.devices = {}
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        """Called when an advertisement packet is received"""
        if addr.addr not in self.devices:
            # New device discovered
            self.devices[addr.addr] = {
                'addr': addr.addr,
                'addr_type': addr.addr_type,
                'rssi': rssi,
                'name': adv_data.name if adv_data.name else "Unknown",
                'data': adv_data
            }
            
            # Print device information
            print(f"\nNew device found:")
            print(f"  Address:    {addr.addr}")
            print(f"  RSSI:       {rssi} dBm")
            print(f"  Name:       {adv_data.name if adv_data.name else 'Unknown'}")
            
            # Show service UUIDs if available
            if hasattr(adv_data, 'service_uuids') and adv_data.service_uuids:
                print(f"  Services:   {', '.join(adv_data.service_uuids)}")
                
            # Show manufacturer data if available
            if hasattr(adv_data, 'manufacturer_specific_data') and adv_data.manufacturer_specific_data:
                print(f"  Mfr Data:   {adv_data.manufacturer_specific_data.hex()}")
        else:
            # Update existing device info
            if rssi != self.devices[addr.addr]['rssi']:
                self.devices[addr.addr]['rssi'] = rssi
                print(f"Updated RSSI for {addr.addr}: {rssi} dBm")
            
            # Update name if previously unknown
            if self.devices[addr.addr]['name'] == "Unknown" and adv_data.name:
                self.devices[addr.addr]['name'] = adv_data.name
                print(f"Updated name for {addr.addr}: {adv_data.name}")

def run_scan(serial_port='/dev/ttyACM0', scan_duration=30):
    """Run a BLE scan for the specified duration"""
    print(f"Starting BLE scan on {serial_port} for {scan_duration} seconds...")
    
    # Initialize the BLE driver
    driver = BLEDriver(serial_port=serial_port, baud_rate=1000000)
    adapter = driver.adapter
    
    # Create and register our scanner observer
    scanner = BLEScanner(adapter)
    adapter.observer_register(scanner)
    
    try:
        # Open and initialize the driver
        driver.open()
        print("Driver opened successfully")
        
        # Configure the BLE adapter
        adapter.driver_init()
        adapter.physical_layer_initialize()
        
        # Configure scan parameters
        scan_params = {
            'active': True,             # Active scanning (requests scan response)
            'interval_ms': 100,         # Scan interval in ms
            'window_ms': 50,            # Scan window in ms
            'timeout_s': scan_duration  # Scan for this many seconds
        }
        
        # Start scanning
        print(f"Scanning for {scan_duration} seconds...")
        adapter.gap_scan_start(**scan_params)
        
        # Wait for the specified duration
        for i in range(scan_duration):
            time.sleep(1)
            sys.stdout.write(".")
            sys.stdout.flush()
            
            # Every 5 seconds, show device count
            if (i+1) % 5 == 0:
                print(f" {len(scanner.devices)} devices found")
        
        # Stop scanning
        adapter.gap_scan_stop()
        print("\nScan complete!")
        
        # Display summary of all devices
        print("\n===== SCAN RESULTS =====")
        print(f"Total devices found: {len(scanner.devices)}")
        
        # Show all devices sorted by signal strength
        devices_by_rssi = sorted(scanner.devices.values(), key=lambda d: d['rssi'], reverse=True)
        for i, device in enumerate(devices_by_rssi):
            print(f"\n{i+1}. {device['name']} ({device['addr']})")
            print(f"   Signal: {device['rssi']} dBm")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Close the driver
        driver.close()
        print("Driver closed")
    
    return scanner.devices

if __name__ == "__main__":
    # Get serial port from command line argument if provided
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyACM0'
    
    # Run the scan
    devices = run_scan(serial_port=port, scan_duration=20)
