import asyncio
from bleak import BleakScanner, BleakClient

async def main():
    # Scan for BLE devices
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

    # Connect to a BLE device (replace with your device's address)
    address = "XX:XX:XX:XX:XX:XX"
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")
        # Read a characteristic (replace with your characteristic UUID)
        value = await client.read_gatt_char("00002a00-0000-1000-8000-00805f9b34fb")
        print(f"Value: {value}")

asyncio.run(main())
