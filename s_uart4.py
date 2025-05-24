#!/usr/bin/env python3
import os, time

# Open for writing and reading separately
with open('/dev/ttyS4', 'wb', buffering=0) as write_port:
    # Set non-blocking mode for the read operation
    read_port = open('/dev/ttyS5', 'rb', buffering=0)
    
    # Send data
    print("Sending test data...")
    write_port.write(b"Test data\n")
    
    # Give time for loopback
    time.sleep(0.5)
    
    # Try to read
    try:
        data = read_port.read(5)
        if data:
            print(f"Received: {data}")
        else:
            print("No data received")
    except Exception as e:
        print(f"Read error: {e}")
    finally:
        read_port.close()
