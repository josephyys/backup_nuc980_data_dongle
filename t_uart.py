#!/usr/bin/env python3
import serial
import threading
import time
import sys
import argparse

# Shared variables
received_data = bytearray()
stop_thread = False

def read_thread_func(ser, timeout_seconds):
    """Thread function to read from serial port character by character"""
    global received_data, stop_thread
    
    start_time = time.time()
    char_count = 0
    
    while not stop_thread and (time.time() - start_time) < timeout_seconds:
        # Read one byte at a time
        if ser.in_waiting > 0:
            byte = ser.read(1)
            if byte:
                char_count += 1
                # Print character information
                char_value = byte[0]
                char_display = chr(char_value) if 32 <= char_value <= 126 else '.'
                print(f"READ[{char_count}]: '{char_display}' (0x{char_value:02x})")
                
                # Store the byte
                received_data.extend(byte)
                
                # Optional: stop after receiving newline
                if byte == b'\n':
                    break
        else:
            # Small delay to prevent CPU thrashing
            time.sleep(0.01)

def test_uart_loopback(port, baud_rate=115200, timeout_seconds=3):
    """Test UART loopback functionality"""
    global received_data, stop_thread
    
    print(f"Testing loopback on {port} at {baud_rate} baud...")
    
    try:
        # Open serial port with appropriate settings
        ser = serial.Serial(
            port=port,
            baudrate=baud_rate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,  # Non-blocking reads
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
        
        # Reset buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Clear shared variables
        received_data = bytearray()
        stop_thread = False
        
        # Start reading thread
        reader = threading.Thread(target=read_thread_func, args=(ser, timeout_seconds))
        reader.start()
        
        # Send test message
        test_msg = b"UART Loopback Test\n"
        print(f"Sending: {test_msg.decode().strip()}")
        ser.write(test_msg)
        
        # Wait for thread to complete
        reader.join(timeout_seconds + 0.5)  # Give a little extra time
        stop_thread = True  # Signal thread to stop if it's still running
        
        # Check results
        if received_data:
            print(f"Complete data received: \"{received_data.decode()}\"")
            print("Loopback test: SUCCESS")
            return True
        else:
            print("No data received.")
            print("Loopback test: FAILED")
            return False
            
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return False
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Test UART loopback connection')
    parser.add_argument('port', nargs='?', default='/dev/ttyS4',
                        help='UART port to test (e.g. /dev/ttyS4, /dev/ttyS5)')
    parser.add_argument('-b', '--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('-t', '--timeout', type=float, default=3.0,
                        help='Read timeout in seconds (default: 3.0)')
    
    args = parser.parse_args()
    
    # Run the test
    success = test_uart_loopback(args.port, args.baud, args.timeout)
    sys.exit(0 if success else 1)
