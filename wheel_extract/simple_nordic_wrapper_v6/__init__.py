
import ctypes
import os
import sys
import time
import threading
# Change it to include c_int8:
from ctypes import POINTER, c_uint8, c_uint16, c_uint32, c_int8, c_void_p, c_char_p, c_bool, Structure, Union, CFUNCTYPE, byref, cast

# Define the library name based on platform
if sys.platform == 'win32':
    LIBRARY_NAME = "nrf_ble_driver_sd_api_v6.dll"
elif sys.platform == 'darwin':
    LIBRARY_NAME = "libnrf_ble_driver_sd_api_v6.dylib"
else:
    LIBRARY_NAME = "libnrf_ble_driver_sd_api_v6.so"

# Try to load the library
try:
    # Try to load from system path first
    _lib = ctypes.CDLL(LIBRARY_NAME)
except OSError:
    # If that fails, try various common locations
    _lib = None
    search_paths = [
        '/usr/lib',
        '/usr/local/lib',
        '/data/usr/lib',
        '/lib',
        '/data',
        os.path.dirname(os.path.abspath(__file__)),
    ]
    for path in search_paths:
        try:
            lib_path = os.path.join(path, LIBRARY_NAME)
            if os.path.exists(lib_path):
                _lib = ctypes.CDLL(lib_path)
                print(f"Found library at {lib_path}")
                break
        except:
            pass
    
    if _lib is None:
        print("WARNING: Could not find Nordic BLE driver library")
        print("The library will need to be available at runtime")
        print(f"Searched paths: {search_paths}")

# Define key constants and enums
NRF_SUCCESS = 0x00
BLE_GAP_ROLE_CENTRAL = 0
BLE_GAP_SCAN_ACTIVE = 1

# Define error checking function
def check_result(result):
    if result != NRF_SUCCESS:
        raise Exception(f"Nordic BLE driver call failed with error code: {result}")

# Define C structures needed for communication
class sd_rpc_ip_addr_t(Structure):
    _fields_ = [
        ("family", c_uint8),
        ("reserved", c_uint8 * 3),
        ("addr", c_uint8 * 16),
    ]

class ble_uuid_t(Structure):
    _fields_ = [
        ("uuid", c_uint16),
        ("type", c_uint8),
    ]

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

class ble_data_t(Structure):
    _fields_ = [
        ("p_data", POINTER(c_uint8)),
        ("len", c_uint16),
    ]

class ble_gap_evt_adv_report_t(Structure):
    _fields_ = [
        ("peer_addr", ble_gap_addr_t),
        ("rssi", c_int8),
        ("scan_rsp", c_uint8),
        ("type", c_uint8),
        ("data", ble_data_t),
    ]

class ble_evt_hdr_t(Structure):
    _fields_ = [
        ("evt_id", c_uint16),
        ("evt_len", c_uint16),
    ]

# Define a dynamic structure for BLE events
class ble_evt_t(Structure):
    _fields_ = [
        ("header", ble_evt_hdr_t),
        # This is a dynamic structure, fields will be accessed based on header.evt_id
    ]

class ble_version_t(Structure):
    _fields_ = [
        ("company_id", c_uint16),
        ("version_number", c_uint16),
        ("subversion_number", c_uint16),
    ]

# Python wrapper for advertising data
class BLEAdvData:
    def __init__(self):
        self.raw_data = b''
        self.name = None
        self.flags = None
        self.service_uuid_count = 0
        self.tx_power_level = None
    
    @staticmethod
    def from_ble_data(ble_data):
        '''Convert C ble_data_t to Python BLEAdvData object.'''
        result = BLEAdvData()
        if not ble_data.p_data:
            return result
            
        # Convert to bytes
        data_length = ble_data.len
        data_ptr = ble_data.p_data
        data_array = bytearray(data_length)
        for i in range(data_length):
            data_array[i] = data_ptr[i]
            
        result.raw_data = bytes(data_array)
        
        # Parse common advertising data fields
        i = 0
        while i < len(result.raw_data):
            if i + 1 >= len(result.raw_data):
                break
                
            field_len = result.raw_data[i]
            if i + 1 + field_len > len(result.raw_data):
                break
                
            if field_len > 0:
                field_type = result.raw_data[i + 1]
                field_data = result.raw_data[i + 2:i + 1 + field_len]
                
                # Complete Local Name (0x09)
                if field_type == 0x09 and field_len > 1:
                    result.name = field_data.decode('utf-8', errors='replace')
                # Flags (0x01)
                elif field_type == 0x01 and field_len > 1:
                    result.flags = field_data[0]
                # TX Power Level (0x0A)
                elif field_type == 0x0A and field_len > 1:
                    result.tx_power_level = field_data[0]
                    if result.tx_power_level > 127:
                        # Convert to signed value
                        result.tx_power_level = result.tx_power_level - 256
                
            i += 1 + field_len
            
        return result

# Observer base classes
class BLEDriverObserver:
    def __init__(self):
        pass

class BLEAdapterObserver:
    def __init__(self):
        pass
        
    def on_gap_evt_adv_report(self, adapter, addr, rssi, adv_type, adv_data):
        pass

# C callback function prototypes
EVT_HANDLER_TYPE = CFUNCTYPE(None, POINTER(ble_evt_t), c_void_p)
STATUS_HANDLER_TYPE = CFUNCTYPE(None, c_uint32, c_char_p, c_void_p)
LOG_HANDLER_TYPE = CFUNCTYPE(None, c_uint32, c_char_p, c_void_p)

# The adapter class for communicating with Nordic dongle
class BLEAdapter:
    def __init__(self, driver):
        self.driver = driver
        self.observers = []
        self._adapter = c_void_p(0)
        
    def driver_init(self):
        print("Initializing BLE adapter")
        
        # Define the required C API function
        if _lib:
            self._adapter = _lib.sd_rpc_adapter_open(self.driver._serial_port.encode(), self.driver._baud_rate, 0, 0)
            if not self._adapter:
                raise Exception("Failed to open adapter")
            return True
        else:
            print("WARNING: Driver library not loaded - simulation mode enabled")
            return True
        
    def physical_layer_initialize(self):
        print("Initializing physical layer")
        if _lib and self._adapter:
            result = _lib.sd_rpc_physical_layer_initialize(self._adapter)
            check_result(result)
            return True
        else:
            print("WARNING: Driver library not loaded - simulation mode enabled")
            return True
        
    def observer_register(self, observer):
        print("Registering observer")
        self.observers.append(observer)
        
    def _on_evt(self, ble_evt, user_data):
        '''C callback for BLE events.'''
        evt_id = ble_evt.contents.header.evt_id
        
        # Handle advertising report event
        if evt_id == 0x10:  # BLE_GAP_EVT_ADV_REPORT
            # Get advertising report data
            adv_report = cast(
                ctypes.addressof(ble_evt.contents) + ctypes.sizeof(ble_evt_hdr_t),
                POINTER(ble_gap_evt_adv_report_t)
            ).contents
            
            # Create Python representation of address
            addr = adv_report.peer_addr
            rssi = adv_report.rssi
            adv_type = adv_report.type
            
            # Convert advertising data
            adv_data = BLEAdvData.from_ble_data(adv_report.data)
            
            # Notify observers
            for observer in self.observers:
                if hasattr(observer, 'on_gap_evt_adv_report'):
                    observer.on_gap_evt_adv_report(self, addr, rssi, adv_type, adv_data)
        
    def gap_scan_start(self, active=True, interval_ms=200, window_ms=150, timeout_s=0):
        print(f"Starting scan: active={active}, interval={interval_ms}ms, window={window_ms}ms, timeout={timeout_s}s")
        
        if _lib and self._adapter:
            # Set up scan parameters
            scan_params = ble_gap_scan_params_t()
            scan_params.active = 1 if active else 0
            scan_params.use_whitelist = 0
            scan_params.interval = interval_ms // 0.625  # Convert to units of 0.625ms
            scan_params.window = window_ms // 0.625  # Convert to units of 0.625ms
            scan_params.timeout = timeout_s  # In seconds
            
            # Register event handler callback
            evt_handler = EVT_HANDLER_TYPE(self._on_evt)
            status_handler = STATUS_HANDLER_TYPE(lambda status, msg, user_data: print(f"Status: {msg.decode()}"))
            log_handler = LOG_HANDLER_TYPE(lambda level, msg, user_data: print(f"Log: {msg.decode()}"))
            
            # Set up event handling
            _lib.sd_rpc_event_handler_set(self._adapter, evt_handler, None)
            _lib.sd_rpc_status_handler_set(self._adapter, status_handler, None)
            _lib.sd_rpc_log_handler_set(self._adapter, log_handler, None)
            
            # Start scanning
            result = _lib.sd_ble_gap_scan_start(self._adapter, byref(scan_params))
            check_result(result)
            return True
        else:
            # Simulation mode for testing without library
            print("WARNING: Using simulation mode for scanning")
            import random
            
            def simulate_devices():
                time.sleep(2)  # Wait a bit before simulating devices
                for i in range(3):  # Simulate 3 devices
                    for observer in self.observers:
                        if hasattr(observer, 'on_gap_evt_adv_report'):
                            addr = ble_gap_addr_t()
                            addr.addr_type = 0
                            for j in range(6):
                                addr.addr[j] = random.randint(0, 255)
                            rssi = -random.randint(40, 90)
                            adv_type = 0
                            adv_data = BLEAdvData()
                            adv_data.name = f"Device_{i}"
                            observer.on_gap_evt_adv_report(self, addr, rssi, adv_type, adv_data)
                    time.sleep(1)
            
            # Start simulation in background thread
            t = threading.Thread(target=simulate_devices)
            t.daemon = True
            t.start()
            return True
        
    def gap_scan_stop(self):
        print("Stopping scan")
        if _lib and self._adapter:
            result = _lib.sd_ble_gap_scan_stop(self._adapter)
            check_result(result)
            return True
        else:
            return True

# The main driver class
class BLEDriver:
    def __init__(self, serial_port, baud_rate=1000000):
        self._serial_port = serial_port
        self._baud_rate = baud_rate
        self._adapter = None
        print(f"Opening connection to {serial_port} at {baud_rate} baud")
    
    def open(self):
        # We'll actually open the connection in driver_init
        return True
        
    def close(self):
        print("Closing BLE connection")
        if _lib and self._adapter and self._adapter._adapter:
            _lib.sd_rpc_adapter_close(self._adapter._adapter)
        return True
    
    @property
    def adapter(self):
        if self._adapter is None:
            self._adapter = BLEAdapter(self)
        return self._adapter
        
    def ble_version_get(self):
        if _lib and self._adapter and self._adapter._adapter:
            # Actually query the version from the device
            version = ble_version_t()
            result = _lib.sd_ble_version_get(self._adapter._adapter, byref(version))
            if result == NRF_SUCCESS:
                return {
                    'company_id': version.company_id,
                    'version_number': version.version_number,
                    'subversion_number': version.subversion_number
                }
        
        # Fallback to hardcoded version if library not loaded
        return {'company_id': 89, 'version_number': 6, 'subversion_number': 1}

# Helper function to format MAC address
def format_addr(addr):
    '''Convert a ble_gap_addr_t to a string MAC address.'''
    if not addr:
        return "00:00:00:00:00:00"
    return ':'.join([f"{addr.addr[i]:02X}" for i in range(5, -1, -1)])

# Enums
class BLEEvtID:
    BLE_GAP_EVT_ADV_REPORT = 0x10
    BLE_GAP_EVT_CONNECTED = 0x11
    BLE_GAP_EVT_DISCONNECTED = 0x12
    BLE_GAP_EVT_TIMEOUT = 0x13
