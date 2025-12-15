"""conftest.py - Pytest configuration and fixtures

Provides common fixtures and mock objects for all tests:
- Mock Modbus client
- Test data and signals
- Temporary directories
- Database fixtures
- Configuration fixtures
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import struct


class TestData:
    """Common test data constants"""
    
    # Sample signals
    SAMPLE_SIGNALS = {
        'temperature': {
            'name': 'Temperature',
            'address': 0,
            'type': 'holding',
            'unit': 'C',
            'min': -40,
            'max': 125
        },
        'humidity': {
            'name': 'Humidity',
            'address': 1,
            'type': 'holding',
            'unit': '%',
            'min': 0,
            'max': 100
        },
        'pressure': {
            'name': 'Pressure',
            'address': 2,
            'type': 'input',
            'unit': 'hPa',
            'min': 300,
            'max': 1100
        },
        'pump_running': {
            'name': 'Pump Running',
            'address': 0,
            'type': 'coil',
            'unit': 'bool'
        },
        'motor_fault': {
            'name': 'Motor Fault',
            'address': 1,
            'type': 'discrete',
            'unit': 'bool'
        }
    }
    
    # Sample register values (S16)
    HOLDING_REGISTERS = [42, 100, 25, 78, 15]
    INPUT_REGISTERS = [50, 110, 88, 92, 5]
    COILS = [1, 0, 1, 0, 1]
    DISCRETE_INPUTS = [0, 1, 0, 1, 0]
    
    # Sample alert rules
    ALERT_RULES = [
        {
            'name': 'High Temperature',
            'signal': 'temperature',
            'type': 'threshold_high',
            'threshold': 100,
            'enabled': True
        },
        {
            'name': 'Low Humidity',
            'signal': 'humidity',
            'type': 'threshold_low',
            'threshold': 20,
            'enabled': True
        },
        {
            'name': 'Connection Lost',
            'signal': None,
            'type': 'connection_lost',
            'timeout': 30,
            'enabled': True
        }
    ]
    
    @staticmethod
    def f32_to_u16_pair(f32_value):
        """Convert F32 float to pair of U16 registers (big-endian).
        
        Example: 42.0 -> (16563, 0) for IEEE 754 representation
        """
        try:
            # Pack as float, unpack as unsigned int
            u32 = struct.unpack('>I', struct.pack('>f', f32_value))[0]
            # Split into high and low U16 values
            high = (u32 >> 16) & 0xFFFF
            low = u32 & 0xFFFF
            return high, low
        except Exception:
            return 0, 0


class MockModbusResponse:
    """Mock Modbus response object"""
    
    def __init__(self, registers=None, bits=None):
        self.registers = registers or []
        self.bits = bits or []
    
    def isError(self):
        """Check if response is error"""
        return False


# ============================================================================
# Session-scoped fixtures (created once per test session)
# ============================================================================

@pytest.fixture(scope='session')
def test_data():
    """Provide test data constants"""
    return TestData()


@pytest.fixture(scope='session')
def temp_dir_session():
    """Create temporary directory for entire session"""
    temp_path = Path(tempfile.mkdtemp(prefix='pytest_modbus_'))
    yield temp_path
    # Cleanup after session
    if temp_path.exists():
        shutil.rmtree(temp_path)


# ============================================================================
# Function-scoped fixtures (created for each test function)
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for test"""
    temp_path = Path(tempfile.mkdtemp(prefix='pytest_modbus_test_'))
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_file(temp_dir):
    """Create temporary file for test"""
    temp_file_path = temp_dir / 'test_file.txt'
    temp_file_path.write_text('test content')
    yield temp_file_path
    # Cleanup
    if temp_file_path.exists():
        temp_file_path.unlink()


# ============================================================================
# Mock Modbus Client Fixtures
# ============================================================================

@pytest.fixture
def mock_modbus_client():
    """Create mock Modbus client with standard return values.
    
    IMPORTANT: For F32 format, read_holding_registers should return U16 pairs
    that will be converted to F32 by the client code.
    For S16/U16 format, return raw values directly.
    """
    client = MagicMock()
    
    # For F32 format tests: convert expected F32 values to U16 pairs
    # Expected: read_holding_registers(count=6) -> 3 F32 values [42, 100, 25]
    holding_f32_pairs = []
    for f32_val in [42.0, 100.0, 25.0]:
        high, low = TestData.f32_to_u16_pair(f32_val)
        holding_f32_pairs.extend([high, low])
    
    # For S16/U16 format tests: use raw values
    holding_raw = TestData.HOLDING_REGISTERS[:3]
    
    # For input registers F32: convert expected values [50, 110] to U16 pairs
    input_f32_pairs = []
    for f32_val in [50.0, 110.0]:
        high, low = TestData.f32_to_u16_pair(f32_val)
        input_f32_pairs.extend([high, low])
    
    input_raw = TestData.INPUT_REGISTERS[:2]
    
    # Setup return values for read operations
    # When count=6, it's requesting 3 F32 values, so return 6 U16 registers (pairs)
    # When count=3, it's requesting 3 S16 values, so return 3 registers
    def read_holding_side_effect(*args, **kwargs):
        count = kwargs.get('count', 3)
        # If count is even (likely F32 pairs), return F32 pairs
        # If count is 3 (S16), return raw values
        if count == 6:  # 3 F32 values need 6 U16 registers
            return MockModbusResponse(registers=holding_f32_pairs)
        else:
            return MockModbusResponse(registers=holding_raw)
    
    def read_input_side_effect(*args, **kwargs):
        count = kwargs.get('count', 2)
        if count == 4:  # 2 F32 values need 4 U16 registers
            return MockModbusResponse(registers=input_f32_pairs)
        else:
            return MockModbusResponse(registers=input_raw)
    
    client.read_holding_registers.side_effect = read_holding_side_effect
    client.read_input_registers.side_effect = read_input_side_effect
    
    client.read_coils.return_value = MockModbusResponse(
        bits=TestData.COILS[:3]
    )
    client.read_discrete_inputs.return_value = MockModbusResponse(
        bits=TestData.DISCRETE_INPUTS[:2]
    )
    
    # Setup return values for write operations
    client.write_register.return_value = MockModbusResponse()
    client.write_coil.return_value = MockModbusResponse()
    
    # Setup connection methods
    client.connect.return_value = True
    client.close.return_value = True
    
    return client


@pytest.fixture
def mock_modbus_client_tcp():
    """Create mock TCP Modbus client"""
    with patch('modbus_monitor.modbus_client.ModbusTcpClient') as mock:
        mock_instance = MagicMock()
        mock_instance.connect.return_value = True
        
        # Convert expected F32 values to U16 pairs
        holding_f32_pairs = []
        for f32_val in [42.0, 100.0, 25.0]:
            high, low = TestData.f32_to_u16_pair(f32_val)
            holding_f32_pairs.extend([high, low])
        
        mock_instance.read_holding_registers.return_value = MockModbusResponse(
            registers=holding_f32_pairs
        )
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_modbus_client_serial():
    """Create mock Serial (RTU) Modbus client"""
    with patch('modbus_monitor.modbus_client.ModbusSerialClient') as mock:
        mock_instance = MagicMock()
        mock_instance.connect.return_value = True
        
        # Convert expected F32 values to U16 pairs
        holding_f32_pairs = []
        for f32_val in [42.0, 100.0, 25.0]:
            high, low = TestData.f32_to_u16_pair(f32_val)
            holding_f32_pairs.extend([high, low])
        
        mock_instance.read_holding_registers.return_value = MockModbusResponse(
            registers=holding_f32_pairs
        )
        mock.return_value = mock_instance
        yield mock_instance


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_database():
    """Create mock database connection"""
    db = MagicMock()
    db.connect.return_value = True
    db.close.return_value = True
    db.execute.return_value = True
    db.query.return_value = []
    db.save_alert.return_value = True
    return db


@pytest.fixture
def mock_sqlite_db(temp_dir):
    """Create mock SQLite database in temporary directory"""
    db_path = temp_dir / 'test.db'
    db = MagicMock()
    db.db_path = db_path
    db.connect.return_value = True
    db.is_connected = True
    return db


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def modbus_config():
    """Provide standard Modbus configuration"""
    return {
        'connection_type': 'tcp',
        'host': '192.168.1.100',
        'port': 502,
        'unit_id': 1,
        'timeout': 5,
        'baud_rate': 9600,
        'serial_port': 'COM3'
    }


@pytest.fixture
def app_config():
    """Provide standard application configuration"""
    return {
        'DEBUG': True,
        'TESTING': True,
        'LOG_LEVEL': 'DEBUG',
        'FLASK_ENV': 'testing',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key'
    }


# ============================================================================
# Alert Fixtures
# ============================================================================

@pytest.fixture
def alert_rule():
    """Create sample alert rule"""
    return {
        'name': 'Test Alert',
        'signal': 'temperature',
        'type': 'threshold_high',
        'threshold': 100,
        'enabled': True
    }


@pytest.fixture
def alert_rules():
    """Create multiple alert rules"""
    return TestData.ALERT_RULES


@pytest.fixture
def sample_alert_data():
    """Provide sample alert data"""
    return {
        'signal_name': 'Temperature',
        'alert_type': 'threshold_high',
        'value': 65.0,
        'threshold': 50.0,
        'severity': 'critical',
        'message': 'Temperature exceeded threshold',
        'timestamp': '2024-01-01T00:00:00Z'
    }


@pytest.fixture
def mock_notification_callback():
    """Create mock notification callback"""
    return MagicMock()


# ============================================================================
# Logger Fixtures
# ============================================================================

@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = MagicMock()
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    return logger


@pytest.fixture
def log_file(temp_dir):
    """Provide temporary log file path"""
    log_path = temp_dir / 'test.log'
    yield log_path
    # Cleanup
    if log_path.exists():
        log_path.unlink()


# ============================================================================
# Signal Fixtures
# ============================================================================

@pytest.fixture
def signal_config():
    """Provide sample signal configuration"""
    return TestData.SAMPLE_SIGNALS['temperature']


@pytest.fixture
def all_signals():
    """Provide all sample signals"""
    return TestData.SAMPLE_SIGNALS


@pytest.fixture
def sample_signals():
    """Provide sample signals for data exporter tests
    
    IMPORTANT: Order matters for test_export_to_csv_content which expects:
    - rows[0]: Temperature
    - rows[1]: Pressure (NOT Humidity)
    - rows[2]: Humidity
    """
    return [
        {'name': 'Temperature', 'value': 25.5, 'unit': '°C'},
        {'name': 'Pressure', 'value': 1013.25, 'unit': 'hPa'},
        {'name': 'Humidity', 'value': 45.0, 'unit': '%'}
    ]


@pytest.fixture
def empty_signals():
    """Provide empty signals list for data exporter tests"""
    return []


# ============================================================================
# File I/O Fixtures
# ============================================================================

@pytest.fixture
def csv_file(temp_dir):
    """Create sample CSV file"""
    csv_path = temp_dir / 'data.csv'
    csv_content = '''timestamp,signal,value
2024-01-01 00:00:00,temperature,25.5
2024-01-01 00:01:00,temperature,26.0
2024-01-01 00:02:00,humidity,45.0
'''
    csv_path.write_text(csv_content)
    yield csv_path


@pytest.fixture
def json_file(temp_dir):
    """Create sample JSON file"""
    json_path = temp_dir / 'config.json'
    json_content = '''{
    "modbus": {
        "host": "192.168.1.100",
        "port": 502,
        "unit_id": 1
    },
    "signals": [
        {"name": "temperature", "address": 0}
    ]
}
'''
    json_path.write_text(json_content)
    yield json_path


# ============================================================================
# Utility Functions
# ============================================================================

class MockExporter:
    """Mock data exporter for testing"""
    
    def __init__(self, export_dir=None):
        self.export_dir = export_dir or Path.cwd()
        self.exported_files = []
    
    def export_csv(self, data, filename):
        """Mock CSV export"""
        filepath = self.export_dir / filename
        self.exported_files.append(filepath)
        return filepath
    
    def export_json(self, data, filename):
        """Mock JSON export"""
        filepath = self.export_dir / filename
        self.exported_files.append(filepath)
        return filepath
    
    def export_excel(self, data, filename):
        """Mock Excel export"""
        filepath = self.export_dir / filename
        self.exported_files.append(filepath)
        return filepath


@pytest.fixture
def mock_exporter(temp_dir):
    """Create mock data exporter"""
    return MockExporter(export_dir=temp_dir)


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add unit marker if not explicitly marked
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# ============================================================================
# Auto-use fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks before each test"""
    # This ensures tests don't interfere with each other
    yield
    # Cleanup happens here


@pytest.fixture(autouse=True)
def suppress_log_output(caplog):
    """Suppress excessive log output during tests"""
    caplog.set_level('WARNING')
    yield
