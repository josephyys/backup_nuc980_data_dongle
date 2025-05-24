# Set up port
stty -F /dev/ttyS5 115200 raw -echo

# First terminal: Monitor RX
cat /dev/ttyS5 &
CAT_PID=$!

# Second terminal: Send data  
echo "Test" > /dev/ttyS5

# Stop monitoring
kill $CAT_PID
