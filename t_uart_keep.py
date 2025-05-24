#!/usr/bin/env python3
import serial
import threading
import time
import sys
import argparse
import queue

# Shared variables
stop_threads = False
rx_queue = queue.Queue()  # Queue for received data

def receiver_thread_func(ser, port_name):
    """Thread function to continuously read from serial port"""
    global stop_threads
    
    char_count = 0
    
    print(f"Receiver thread started for {port_name}")
    
    while not stop_threads:
        # Read one byte at a time
        if ser.in_waiting > 0:
            byte = ser.read(1)
            if byte:
                char_count += 1
                # Print character information
                char_value = byte[0]
                char_display = chr(char_value) if 32 <= char_value <= 126 else '.'
                print(f"READ[{char_count}]: '{char_display}' (0x{char_value:02x})")
                
                # Add to queue for processing if needed
                rx_queue.put(byte)
        else:
            # Small delay to prevent CPU thrashing
            time.sleep(0.01)
    
    print(f"Receiver thread for {port_name} stopped")

def sender_thread_func(ser, port_name, interval=1.0):
    """Thread function to periodically send test messages"""
    global stop_threads
    
    msg_count = 0
    
    print(f"Sender thread started for {port_name}")
    
    while not stop_threads:
        # Create message with sequence number
        msg_count += 1
        test_msg = f"UART Test #{msg_count} at {time.time():.1f}\n".encode()
        
        # Send the message
        print(f"SENDING[{msg_count}]: {test_msg.decode().strip()}")
        ser.write(test_msg)
        
        # Wait for next interval
        time.sleep(interval)
    
    print(f"Sender thread for {port_name} stopped")

def test_uart_continuous(port, baud_rate=115200, send_interval=2.0, run_duration=30):
    """Test UART with continuous sending and receiving"""
    global stop_threads
    
    print(f"Starting continuous UART test on {port} at {baud_rate} baud...")
    print(f"Send interval: {send_interval} seconds, Run duration: {run_duration} seconds")
    
    try:
        # Open serial port
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
        
        # Clear stop flag
        stop_threads = False
        
        # Start receiver thread
        receiver = threading.Thread(target=receiver_thread_func, args=(ser, port))
        receiver.start()
        
        # Start sender thread
        sender = threading.Thread(target=sender_thread_func, args=(ser, port, send_interval))
        sender.start()
        
        # Run for specified duration or until Ctrl+C
        print(f"Test running for {run_duration} seconds (Ctrl+C to stop early)...")
        try:
            time.sleep(run_duration)
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
        
        # Signal threads to stop and wait for them
        stop_threads = True
        receiver.join(timeout=2.0)
        sender.join(timeout=2.0)
        
        print("UART test completed")
            
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return False
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"Closed {port}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Continuous UART test with separate send/receive threads')
    parser.add_argument('port', nargs='?', default='/dev/ttyS4',
                        help='UART port to test (e.g. /dev/ttyS4, /dev/ttyS5)')
    parser.add_argument('-b', '--baud', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('-i', '--interval', type=float, default=2.0,
                        help='Send interval in seconds (default: 2.0)')
    parser.add_argument('-d', '--duration', type=int, default=30,
                        help='Test duration in seconds (default: 30)')
    
    args = parser.parse_args()
    
    # Run the test
    test_uart_continuous(args.port, args.baud, args.interval, args.duration)
