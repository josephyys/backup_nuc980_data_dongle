#!/usr/bin/env python3
import ctypes
import re

lib = ctypes.CDLL("/data/usr/lib/libnrf-ble-driver-sd_api_v5.so")
functions = [f for f in dir(lib) if not f.startswith('_')]
print("Available functions:")
for f in sorted(functions):
    print(f)

print("\nMatching 'open':")
for f in sorted(functions):
    if "open" in f.lower():
        print(f)
