#!/usr/bin/env python
"""
test_modbus_server.py - Test Modbus TCP Server

Provides a mock Modbus device for testing and development.
Useful when you don't have a real Modbus device connected.

Usage:
    python test_modbus_server.py

Then connect from dashboard:
    Host: localhost
    Port: 5020
    Type: tcp
"""

import time
import threading
import random
from datetime import datetime

try:
    from pymodbus.server import StartTcpServer
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.datastore import ModbusSequentialDataStore
    from pymodbus.datastore import ModbusServerContext
except ImportError:
    print("\n❌ Error: pymodbus not installed")
    print("Install it with: pip install pymodbus")
    exit(1)

class MockModbusValues:
    """Generates mock Modbus register values"""
    
    def __init__(self):
        self.values = {
            'holding': {},
            'input': {},
            'coils': {},
            'discrete': {}
        }
        self.init_values()
    
    def init_values(self):
        """Initialize registers with default values"""
        # Holding registers (0-10)
        for i in range(11):
            self.values['holding'][i] = 100 + i * 10
        
        # Input registers (0-10)
        for i in range(11):
            self.values['input'][i] = 50 + i * 5
        
        # Coils (0-10)
        for i in range(11):
            self.values['coils'][i] = i % 2 == 0
        
        # Discrete inputs (0-10)
        for i in range(11):
            self.values['discrete'][i] = i % 3 == 0
    
    def update_values(self):
        """Simulate changing values"""
        # Add some variation to holding registers
        for i in range(11):
            base = 100 + i * 10
            variation = random.randint(-5, 5)
            self.values['holding'][i] = base + variation
            
            # Input registers with different pattern
            base_input = 50 + i * 5
            variation_input = random.randint(-3, 3)
            self.values['input'][i] = base_input + variation_input
        
        # Toggle some coils
        for i in range(11):
            if random.random() > 0.7:
                self.values['coils'][i] = not self.values['coils'][i]
    
    def get_register(self, register_type, address):
        """Get a register value"""
        try:
            return self.values[register_type].get(address, 0)
        except:
            return 0

def create_test_datastore():
    """
    Create a Modbus datastore with test data.
    Uses in-memory storage.
    """
    
    # Create mock values
    mock = MockModbusValues()
    
    # Initialize stores
    store = ModbusSequentialDataStore(
        di=[False] * 100,      # Discrete inputs
        co=[False] * 100,      # Coils
        hr=[0] * 100,          # Holding registers
        ir=[0] * 100           # Input registers
    )
    
    # Populate with test data
    for i in range(11):
        store.setValues(3, i, [mock.values['holding'][i]])     # Holding (address 0-10)
        store.setValues(4, i, [mock.values['input'][i]])       # Input (address 0-10)
        store.setValues(1, i, [int(mock.values['coils'][i])])  # Coils (address 0-10)
        store.setValues(2, i, [int(mock.values['discrete'][i])])  # Discrete (address 0-10)
    
    # Create context
    context = ModbusServerContext(stores={0x00: store}, single=False)
    
    return context, mock

def update_datastore(context, mock, stop_event):
    """
    Continuously update datastore with new values.
    Simulates a real Modbus device generating data.
    """
    store = context[0x00]
    
    while not stop_event.is_set():
        # Update mock values
        mock.update_values()
        
        # Write to store
        for i in range(11):
            store.setValues(3, i, [mock.values['holding'][i]])     # Holding
            store.setValues(4, i, [mock.values['input'][i]])       # Input
            store.setValues(1, i, [int(mock.values['coils'][i])])  # Coils
            store.setValues(2, i, [int(mock.values['discrete'][i])])  # Discrete
        
        time.sleep(1)  # Update every second

def main():
    """
    Start the test Modbus TCP server.
    """
    
    print("\n" + "="*70)
    print("🧪 Test Modbus TCP Server")
    print("="*70)
    print()
    print("📄 Configuration:")
    print("  • Host: localhost (127.0.0.1)")
    print("  • Port: 5020")
    print("  • Type: TCP")
    print()
    print("📊 Available Registers:")
    print("  • Holding Registers (0-10): Values 100-200")
    print("  • Input Registers (0-10): Values 50-100")
    print("  • Coils (0-10): Boolean values")
    print("  • Discrete Inputs (0-10): Boolean values")
    print()
    print("🚀 Server Status: STARTING...\n")
    print("="*70)
    print()
    print("💽 Usage in Dashboard:")
    print("  1. Open http://localhost:5000")
    print("  2. Enter connection parameters:")
    print("     - Host: localhost")
    print("     - Port: 5020")
    print("     - Type: tcp")
    print("  3. Click 'Connect'")
    print("  4. You should see signals updating!")
    print()
    print("⚠️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    try:
        # Create datastore
        context, mock = create_test_datastore()
        
        # Create device identification
        identity = ModbusDeviceIdentification(
            info_name='Test Modbus Server',
            info_code='Test',
            info_url='http://localhost:5020'
        )
        
        # Create stop event
        stop_event = threading.Event()
        
        # Start update thread
        update_thread = threading.Thread(
            target=update_datastore,
            args=(context, mock, stop_event),
            daemon=True
        )
        update_thread.start()
        
        # Start TCP server
        print("✅ Test Modbus TCP Server RUNNING on localhost:5020")
        print(f"🖮 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        StartTcpServer(
            context=context,
            identity=identity,
            address=("localhost", 5020),
            allow_reuse_address=True
        )
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        stop_event.set()
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("💻 Cleanup...")
        print("="*70)

if __name__ == "__main__":
    main()
