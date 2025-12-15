#!/usr/bin/env python
"""
test_modbus_client.py - Unit Tests for ModbusClientManager

Tests cover:
- Connection management (TCP/RTU)
- Register reading (holding, input, coil, discrete)
- Register writing
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modbus_monitor.modbus_client import ModbusClientManager


@pytest.mark.unit
class TestModbusClientManagerInit:
    """Test ModbusClientManager initialization"""
    
    def test_init_defaults(self):
        """Test default initialization"""
        client = ModbusClientManager()
        
        assert client.client is None
        assert client.connection_type == 'tcp'
        assert client.unit_id == 1
        assert client.is_connected is False
    
    def test_init_creates_instance(self):
        """Test that instance is created properly"""
        client = ModbusClientManager()
        
        assert isinstance(client, ModbusClientManager)
        assert hasattr(client, 'connect')
        assert hasattr(client, 'disconnect')
        assert hasattr(client, 'read_registers')
        assert hasattr(client, 'write_register')


@pytest.mark.unit
class TestModbusClientManagerConnection:
    """Test Modbus connection management"""
    
    @patch('modbus_monitor.modbus_client.ModbusTcpClient')
    def test_connect_tcp_success(self, mock_tcp_client_class, mock_modbus_client):
        """Test successful TCP connection"""
        # Setup mock
        mock_tcp_client_class.return_value = mock_modbus_client
        mock_modbus_client.connect.return_value = True
        
        client = ModbusClientManager()
        result = client.connect(
            host='192.168.1.100',
            port=502,
            connection_type='tcp',
            unit_id=1
        )
        
        assert result is True
        assert client.is_connected is True
        assert client.connection_type == 'tcp'
        assert client.unit_id == 1
    
    @patch('modbus_monitor.modbus_client.ModbusTcpClient')
    def test_connect_tcp_failure(self, mock_tcp_client_class, mock_modbus_client):
        """Test failed TCP connection"""
        # Setup mock for failed connection
        mock_tcp_client_class.return_value = mock_modbus_client
        mock_modbus_client.connect.return_value = False
        
        client = ModbusClientManager()
        result = client.connect(
            host='192.168.1.100',
            port=502,
            connection_type='tcp'
        )
        
        assert result is False
        assert client.is_connected is False
    
    @patch('modbus_monitor.modbus_client.ModbusSerialClient')
    def test_connect_serial_success(self, mock_serial_client_class, mock_modbus_client):
        """Test successful serial (RTU) connection"""
        # Setup mock
        mock_serial_client_class.return_value = mock_modbus_client
        mock_modbus_client.connect.return_value = True
        
        client = ModbusClientManager()
        result = client.connect(
            connection_type='serial',
            serial_port='COM3',
            baud_rate=9600
        )
        
        assert result is True
        assert client.connection_type == 'serial'
    
    def test_disconnect(self, mock_modbus_client):
        """Test disconnection"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        client.disconnect()
        
        mock_modbus_client.close.assert_called_once()
        assert client.is_connected is False
    
    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected"""
        client = ModbusClientManager()
        client.client = None
        client.is_connected = False
        
        # Should not raise exception
        client.disconnect()
        assert client.is_connected is False


@pytest.mark.unit
class TestModbusClientManagerReadRegisters:
    """Test register reading operations"""
    
    def test_read_holding_registers_success(self, mock_modbus_client):
        """Test reading holding registers"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.read_registers(
            address=0,
            count=3,
            register_type='holding'
        )
        
        assert result == [42, 100, 25]
        mock_modbus_client.read_holding_registers.assert_called_once()
    
    def test_read_input_registers_success(self, mock_modbus_client):
        """Test reading input registers"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.read_registers(
            address=0,
            count=2,
            register_type='input'
        )
        
        assert result == [50, 110]
        mock_modbus_client.read_input_registers.assert_called_once()
    
    def test_read_coils_success(self, mock_modbus_client):
        """Test reading coils"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.read_registers(
            address=0,
            count=3,
            register_type='coil'
        )
        
        assert result == [1, 0, 1]
        mock_modbus_client.read_coils.assert_called_once()
    
    def test_read_discrete_inputs_success(self, mock_modbus_client):
        """Test reading discrete inputs"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.read_registers(
            address=0,
            count=2,
            register_type='discrete'
        )
        
        assert result == [0, 1]
        mock_modbus_client.read_discrete_inputs.assert_called_once()
    
    def test_read_registers_not_connected(self):
        """Test reading when not connected"""
        client = ModbusClientManager()
        client.is_connected = False
        
        result = client.read_registers(address=0, count=1)
        
        assert result is None
    
    def test_read_registers_invalid_type(self, mock_modbus_client):
        """Test reading with invalid register type"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.read_registers(
            address=0,
            count=1,
            register_type='invalid_type'
        )
        
        assert result is None
    
    def test_read_registers_with_unit_id(self, mock_modbus_client):
        """Test that unit_id is passed correctly"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        client.unit_id = 5
        
        client.read_registers(address=0, count=1, register_type='holding')
        
        # Verify unit_id was passed
        call_kwargs = mock_modbus_client.read_holding_registers.call_args[1]
        assert call_kwargs['unit'] == 5


@pytest.mark.unit
class TestModbusClientManagerWriteRegisters:
    """Test register writing operations"""
    
    def test_write_holding_register_success(self, mock_modbus_client):
        """Test writing holding register"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.write_register(
            address=0,
            value=100,
            register_type='holding'
        )
        
        assert result is True
        mock_modbus_client.write_register.assert_called_once()
    
    def test_write_coil_success(self, mock_modbus_client):
        """Test writing coil"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.write_register(
            address=0,
            value=1,
            register_type='coil'
        )
        
        assert result is True
        mock_modbus_client.write_coil.assert_called_once()
    
    def test_write_register_not_connected(self):
        """Test writing when not connected"""
        client = ModbusClientManager()
        client.is_connected = False
        
        result = client.write_register(address=0, value=100)
        
        assert result is False
    
    def test_write_register_invalid_type(self, mock_modbus_client):
        """Test writing with invalid register type"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        result = client.write_register(
            address=0,
            value=100,
            register_type='invalid'
        )
        
        assert result is False
    
    def test_write_register_with_unit_id(self, mock_modbus_client):
        """Test that unit_id is passed during write"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        client.unit_id = 3
        
        client.write_register(address=0, value=50, register_type='holding')
        
        # Verify unit_id was passed
        call_kwargs = mock_modbus_client.write_register.call_args[1]
        assert call_kwargs['unit'] == 3


@pytest.mark.unit
class TestModbusClientManagerErrorHandling:
    """Test error handling"""
    
    @patch('modbus_monitor.modbus_client.ModbusTcpClient')
    def test_connect_handles_exception(self, mock_tcp_client_class):
        """Test exception handling during connection"""
        mock_tcp_client_class.side_effect = Exception("Connection failed")
        
        client = ModbusClientManager()
        result = client.connect(host='192.168.1.100', port=502)
        
        assert result is False
        assert client.is_connected is False
    
    def test_read_registers_handles_exception(self, mock_modbus_client):
        """Test exception handling during read"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        # Mock to raise exception
        mock_modbus_client.read_holding_registers.side_effect = Exception("Read failed")
        
        result = client.read_registers(address=0, count=1)
        
        assert result is None
    
    def test_write_register_handles_exception(self, mock_modbus_client):
        """Test exception handling during write"""
        client = ModbusClientManager()
        client.client = mock_modbus_client
        client.is_connected = True
        
        # Mock to raise exception
        mock_modbus_client.write_register.side_effect = Exception("Write failed")
        
        result = client.write_register(address=0, value=100)
        
        assert result is False
