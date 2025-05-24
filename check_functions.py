#!/usr/bin/env python3
import ctypes
import sys

try:
    # Try to load the library
    lib = ctypes.CDLL("/data/usr/lib/libnrf_ble_driver_sd_api_v5.so")
    
    # List all available functions with 'physical' in the name
    physical_funcs = [name for name in dir(lib) if 'physical' in name.lower()]
    print("Functions with 'physical' in the name:")
    for func in sorted(physical_funcs):
        print(f"  {func}")
        
    # List all available functions with 'conn' in the name
    conn_funcs = [name for name in dir(lib) if 'conn' in name.lower()]
    print("\nFunctions with 'conn' in the name:")
    for func in sorted(conn_funcs):
        print(f"  {func}")
    
    # List all initialization-related functions
    init_funcs = [name for name in dir(lib) if 'init' in name.lower()]
    print("\nFunctions with 'init' in the name:")
    for func in sorted(init_funcs):
        print(f"  {func}")
    
except Exception as e:
    print(f"Error: {e}")
