#!/usr/bin/env python3
import serial
import time

def test_single_port_loopback(uart_dev: str, baud: int = 115200, timeout: float = 1.0):
    """
    Open a single UART port, send a message, and verify it loops back.
    :param uart_dev: device path (e.g. '/dev/ttyS4')
    :param baud: baud rate
    :param timeout: read timeout in seconds
    """
    try:
        # Open serial port
        ser = serial.Serial(
            port=uart_dev,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        # Flush buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Test message
        msg = b"Loopback Test\n"
        print(f"Sending: {msg.strip().decode()}")

        # Send and allow time to loop back
        ser.write(msg)
        time.sleep(0.1)

        # Read back
        response = ser.readline()
        if response:
            print(f"Received: {response.strip().decode()}")
            print("Loopback test: SUCCESS")
        else:
            print("Loopback test: FAILED (no data received)")

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    # Replace with your UART port
    test_single_port_loopback('/dev/ttyS4')

