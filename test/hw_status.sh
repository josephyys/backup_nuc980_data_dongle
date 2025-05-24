# Check USB device info
lsusb | grep -i Nordic

# Check kernel recognition
dmesg | grep -i nordic
dmesg | grep ttyACM

# Check device permissions
ls -la /dev/ttyACM0
