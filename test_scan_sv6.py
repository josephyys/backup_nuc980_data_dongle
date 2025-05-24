#!/usr/bin/env python3
import sys
import time
from simple_nordic_wrapper_v6 import BLEDriver, BLEAdapterObserver

class ScanObserver(BLEAdapterObserver):
    def __init__(self):
        super(ScanObserver, self).__init__()
        self.devices = {}
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        addr_str = ':'.join([f"{addr.addr[i]:02X}" for i in range(5, -1, -1)])
        print(f"DEVICE: {addr_str}, RSSI: {rssi}, Name: {adv_data.name}")
        self.devices[addr_str] = (rssi, adv_data.name)

# Create driver with your dongle's serial port
driver = BLEDriver('/dev/ttyACM0', baud_rate=1000000)
driver.open()

# Initialize adapter
adapter = driver.adapter

# Create and register observer
observer = ScanObserver()
adapter.observer_register(observer)

# Query version
version = driver.ble_version_get()
print(f"Connected to device with firmware version: {version['version_number']}.{version['subversion_number']}")

# Initialize and scan
adapter.driver_init()
adapter.physical_layer_initialize()
adapter.gap_scan_start(active=True, interval_ms=30, window_ms=20, timeout_s=0)

# Run for 30 seconds
try:
    for i in range(30):
        time.sleep(1)
        print(f"Scanning... {i+1}/30s, {len(observer.devices)} devices found", end="\r")
except KeyboardInterrupt:
    print("\nScan interrupted")

# Clean up
adapter.gap_scan_stop()
driver.close()
print("\nComplete - devices found:", len(observer.devices))

