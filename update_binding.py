#!/usr/bin/env python3

import os
import sys
import re

def update_binding(binding_dir):
    """Update the binding to use the correct function names."""
    init_file = os.path.join(binding_dir, "__init__.py")
    
    if not os.path.exists(init_file):
        print(f"Error: {init_file} not found")
        return False
    
    # Read the file
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Make replacements for function names
    replacements = [
        # For adapter initialization
        (r'self\._adapter\s*=\s*_lib\.sd_rpc_adapter_open\(', 
         'self._adapter = _lib.sd_rpc_adapter_create('),
         
        # For physical layer
        (r'result\s*=\s*_lib\.sd_rpc_physical_layer_initialize\(self\._adapter\)',
         '# Create physical layer first\n'
         '        phy = _lib.sd_rpc_physical_layer_create_uart(self.driver._serial_port.encode(), self.driver._baud_rate)\n'
         '        if not phy:\n'
         '            raise Exception("Failed to create physical layer")\n'
         '        # Setup transport and data link layers (simplified)\n'
         '        transport = _lib.sd_rpc_transport_layer_create(phy, 0)\n'
         '        if not transport:\n'
         '            raise Exception("Failed to create transport layer")\n'
         '        # Now reset connection\n'
         '        result = _lib.sd_rpc_conn_reset(self._adapter)'),
    ]
    
    # Apply replacements
    updated_content = content
    for pattern, replacement in replacements:
        updated_content = re.sub(pattern, replacement, updated_content)
    
    # Add c_int8 to imports if missing
    if 'c_int8' not in updated_content:
        updated_content = updated_content.replace(
            'from ctypes import POINTER, c_uint8, c_uint16, c_uint32',
            'from ctypes import POINTER, c_uint8, c_uint16, c_uint32, c_int8')
    
    # Write the updated file
    with open(init_file, 'w') as f:
        f.write(updated_content)
    
    print(f"Updated {init_file} with correct function names")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_binding.py /path/to/binding/directory")
        sys.exit(1)
    
    binding_dir = sys.argv[1]
    if update_binding(binding_dir):
        print("Successfully updated binding!")
    else:
        print("Failed to update binding")
