#!/bin/sh

# Configure both UARTs with the same settings
stty -F /dev/ttyS4 115200 raw -echo
stty -F /dev/ttyS5 115200 raw -echo

# Start monitoring UART5 in the background
cat /dev/ttyS5 > /tmp/uart_test.txt &
CAT_PID=$!

# Wait a moment for the background process to start
sleep 1

# Send a test message from UART4
echo "UART Loopback Test" > /dev/ttyS4

# Wait for data to transfer
sleep 1

# Stop the background process
kill $CAT_PID

# Check the results
echo "Received data:"
cat /tmp/uart_test.txt

# Clean up
rm /tmp/uart_test.txt
