#!/usr/bin/env python
"""
conftest.py - Pytest Configuration and Shared Fixtures

This file provides reusable fixtures and configurations for all unit tests.
"""

import pytest
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# ============================================================================
# SESSION FIXTURES (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def temp_export_dir():
    """Create temporary directory for export tests"""
    temp_dir = tempfile.mkdtemp(prefix="modbus_export_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def temp_db_dir():
    """Create temporary directory for database tests"""
    temp_dir = tempfile.mkdtemp(prefix="modbus_db_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# ============================================================================
# FUNCTION FIXTURES (run before each test function)
# ============================================================================

@pytest.fixture
def sample_signals():
    """Sample signal data for testing"""
    return [
        {
            'id': 1,
            'address': 0,
            'name': 'Temperature',
            'value': 42.5,
            'unit': '\u00b0C',
            'status': 'ok',
            'lastUpdate': '2025-12-15 10:30:00'
        },
        {
            'id': 2,
            'address': 1,
            'name': 'Pressure',
            'value': 100.0,
            'unit': 'bar',
            'status': 'ok',
            'lastUpdate': '2025-12-15 10:30:00'
        },
        {
            'id': 3,
            'address': 2,
            'name': 'Flow',
            'value': 25.3,
            'unit': 'L/min',
            'status': 'ok',
            'lastUpdate': '2025-12-15 10:30:00'
        },
    ]


@pytest.fixture
def empty_signals():
    """Empty signals list"""
    return []


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    from datetime import datetime
    return {
        'signal_name': 'Temperature',
        'alert_type': 'threshold_high',
        'message': 'Temperature exceeded 50°C',
        'severity': 'critical',
        'value': 55.0,
        'timestamp': datetime.now()
    }


@pytest.fixture
def mock_modbus_client():
    """Mock Modbus client for testing without real hardware"""
    mock_client = Mock()
    mock_client.connect = Mock(return_value=True)
    mock_client.close = Mock(return_value=True)
    mock_client.read_holding_registers = Mock(
        return_value=Mock(registers=[42, 100, 25], isError=Mock(return_value=False))
    )
    mock_client.read_input_registers = Mock(
        return_value=Mock(registers=[50, 110], isError=Mock(return_value=False))
    )
    mock_client.read_coils = Mock(
        return_value=Mock(bits=[1, 0, 1], isError=Mock(return_value=False))
    )
    mock_client.read_discrete_inputs = Mock(
        return_value=Mock(bits=[0, 1], isError=Mock(return_value=False))
    )
    mock_client.write_register = Mock(
        return_value=Mock(isError=Mock(return_value=False))
    )
    mock_client.write_coil = Mock(
        return_value=Mock(isError=Mock(return_value=False))
    )
    return mock_client


@pytest.fixture
def mock_database():
    """Mock database for testing"""
    mock_db = Mock()
    mock_db.save_signal = Mock(return_value=True)
    mock_db.save_alert = Mock(return_value=True)
    mock_db.get_alerts = Mock(return_value=[])
    mock_db.get_signals = Mock(return_value=[])
    mock_db.close = Mock(return_value=True)
    return mock_db


@pytest.fixture
def mock_notification_callback():
    """Mock notification callback"""
    return Mock(return_value=None)


# ============================================================================
# PYTEST HOOKS AND CONFIGURATION
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
        "markers", "slow: mark test as slow running"
    )


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_signals(count=5, value_range=(0, 100)):
        """Generate sample signals"""
        signals = []
        for i in range(count):
            signals.append({
                'id': i + 1,
                'address': i,
                'name': f'Signal_{i+1}',
                'value': (value_range[0] + value_range[1]) / 2,
                'unit': 'units',
                'status': 'ok',
                'lastUpdate': '2025-12-15 10:30:00'
            })
        return signals
    
    @staticmethod
    def generate_alert_rules(count=3):
        """Generate sample alert rules"""
        from modbus_monitor.modbus_alerts import AlertRule
        rules = []
        for i in range(count):
            rules.append(
                AlertRule(
                    signal_name=f'Signal_{i+1}',
                    alert_type='threshold_high',
                    threshold=80.0,
                    enabled=True,
                    severity='warning'
                )
            )
        return rules


@pytest.fixture
def test_data_generator():
    """Provide test data generator"""
    return TestDataGenerator()
