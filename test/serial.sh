# Try reading raw data from the device
cat /dev/ttyACM0 > raw_output.bin &
CAT_PID=$!
sleep 2
kill $CAT_PID

# Check if any data was captured
hexdump -C raw_output.bin | head
