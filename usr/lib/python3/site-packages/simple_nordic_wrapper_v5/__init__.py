
import ctypes
import os
import sys
from ctypes import POINTER, c_uint8, c_uint16, c_uint32, c_int8, c_void_p, c_char_p, Structure, byref

# Library name and loading
if sys.platform == 'win32':
    LIBRARY_NAME = "nrf_ble_driver_sd_api_v5.dll"
elif sys.platform == 'darwin':
    LIBRARY_NAME = "libnrf_ble_driver_sd_api_v5.dylib"
else:
    LIBRARY_NAME = "libnrf-ble-driver-sd_api_v5.so"

try:
    _lib = ctypes.CDLL(LIBRARY_NAME)
except OSError:
    _lib = None
    search_paths = [
        '/usr/lib', '/usr/local/lib', '/data/usr/lib', '/lib', '/data',
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for path in search_paths:
        try:
            lib_path = os.path.join(path, LIBRARY_NAME)
            if os.path.exists(lib_path):
                _lib = ctypes.CDLL(lib_path)
                print(f"Found library at {lib_path}")
                break
        except Exception:
            pass
    if _lib is None:
        print("WARNING: Could not find Nordic BLE driver library")
        print(f"Searched paths: {search_paths}")

NRF_SUCCESS = 0x00

def check_result(result):
    if result != NRF_SUCCESS:
        raise Exception(f"Nordic BLE driver call failed with error code: {result}")

# C structures
class ble_gap_addr_t(Structure):
    _fields_ = [
        ("addr_type", c_uint8),
        ("addr", c_uint8 * 6),
    ]

class ble_gap_scan_params_t(Structure):
    _fields_ = [
        ("active", c_uint8),
        ("use_whitelist", c_uint8),
        ("interval", c_uint16),
        ("window", c_uint16),
        ("timeout", c_uint16),
    ]

class ble_gap_evt_adv_report_t(Structure):
    _fields_ = [
        ("peer_addr", ble_gap_addr_t),
        ("rssi", c_int8),
        ("scan_rsp", c_uint8),
        ("type", c_uint8),
        ("dlen", c_uint16),
        ("data", POINTER(c_uint8)),
    ]

class ble_evt_hdr_t(Structure):
    _fields_ = [
        ("evt_id", c_uint16),
        ("evt_len", c_uint16),
    ]

class ble_evt_t(Structure):
    _fields_ = [
        ("header", ble_evt_hdr_t),
        # ... dynamic fields ...
    ]

class ble_version_t(Structure):
    _fields_ = [
        ("company_id", c_uint16),
        ("version_number", c_uint16),
        ("subversion_number", c_uint16),
    ]

# Helper to format MAC address
def format_addr(addr):
    return ':'.join([f"{addr.addr[i]:02X}" for i in range(5, -1, -1)])

# BLE event handler (Python version)
def ble_evt_handler(adapter, p_ble_evt):
    evt_id = p_ble_evt.contents.header.evt_id
    if evt_id == 0x10:  # BLE_GAP_EVT_ADV_REPORT
        adv_report = ctypes.cast(
            ctypes.addressof(p_ble_evt.contents) + ctypes.sizeof(ble_evt_hdr_t),
            POINTER(ble_gap_evt_adv_report_t)
        ).contents
        print_adv_report(adv_report)

def print_adv_report(adv_report):
    print(f"Device: {format_addr(adv_report.peer_addr.addr)}, RSSI: {adv_report.rssi}", end='')
    # Parse advertising data for name
    data = ctypes.string_at(adv_report.data, adv_report.dlen)
    pos = 0
    name = None
    while pos < adv_report.dlen:
        field_len = data[pos]
        if field_len == 0 or pos + 1 + field_len > adv_report.dlen:
            break
        field_type = data[pos + 1]
        if field_type == 0x09 and field_len > 1:
            name = data[pos + 2:pos + 1 + field_len].decode('utf-8', errors='replace')
            break
        pos += 1 + field_len
    if name:
        print(f", Name: {name}")
    else:
        print()

# Main BLE driver class
class BLEDriver:
    def __init__(self, serial_port, baud_rate=1000000):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.adapter = None

    def open(self):
        if not _lib:
            raise RuntimeError("BLE driver library not loaded")
        # Create physical/data/transport layers and adapter as in C code
        phy = _lib.sd_rpc_physical_layer_create_uart(self.serial_port.encode(), self.baud_rate, 0, 0)
        if not phy:
            raise Exception("Failed to create physical layer")
        data_link = _lib.sd_rpc_data_link_layer_create_bt_three_wire(phy, 250)
        if not data_link:
            raise Exception("Failed to create data link layer")
        transport = _lib.sd_rpc_transport_layer_create(data_link, 1500)
        if not transport:
            raise Exception("Failed to create transport layer")
        self.adapter = _lib.sd_rpc_adapter_create(transport)
        if not self.adapter:
            raise Exception("Failed to create adapter")
        # Set up handler types
        STATUS_HANDLER_TYPE = ctypes.CFUNCTYPE(None, c_void_p, c_uint32, c_char_p)
        EVT_HANDLER_TYPE = ctypes.CFUNCTYPE(None, c_void_p, POINTER(ble_evt_t))
        LOG_HANDLER_TYPE = ctypes.CFUNCTYPE(None, c_void_p, c_uint32, c_char_p)
        # Register handlers (dummy for now)
        status_handler = STATUS_HANDLER_TYPE(lambda a, s, m: print(f"STATUS: {m.decode()}"))
        evt_handler = EVT_HANDLER_TYPE(ble_evt_handler)
        log_handler = LOG_HANDLER_TYPE(lambda a, s, m: print(f"LOG: {m.decode()}"))
        # Open adapter
        result = _lib.sd_rpc_open(self.adapter, status_handler, evt_handler, log_handler)
        check_result(result)
        # Enable BLE stack
        result = _lib.sd_ble_enable(self.adapter, None)
        check_result(result)
        # Print version
        version = ble_version_t()
        result = _lib.sd_ble_version_get(self.adapter, byref(version))
        if result == NRF_SUCCESS:
            print(f"SoftDevice version: {version.version_number}.{version.subversion_number} (company: {version.company_id})")

    def scan(self):
        scan_params = ble_gap_scan_params_t(
            active=1, use_whitelist=0, interval=0x00A0, window=0x0050, timeout=0
        )
        result = _lib.sd_ble_gap_scan_start(self.adapter, byref(scan_params))
        check_result(result)
        print("Scanning... (press Ctrl+C to stop)")
        # In real code, events would be handled by the event handler above

    def close(self):
        if self.adapter:
            _lib.sd_rpc_close(self.adapter)
            _lib.sd_rpc_adapter_delete(self.adapter)
            self.adapter = None

# Usage example:
# driver = BLEDriver("/dev/ttyACM0")
# driver.open()
# driver.scan()
# driver.close()
