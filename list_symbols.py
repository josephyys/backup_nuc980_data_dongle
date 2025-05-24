#!/usr/bin/env python3
import ctypes
import sys

try:
    lib = ctypes.CDLL("/data/usr/lib/libnrf_ble_driver_sd_api_v6.so")
    print("Library loaded successfully")
    # List all available sd_rpc functions
    for attr in dir(lib):
        if attr.startswith("sd_rpc"):
            print(attr)
except Exception as e:
    print(f"Error: {e}")
