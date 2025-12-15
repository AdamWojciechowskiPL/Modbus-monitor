# modbus_client.py - Klient Modbus TCP/Serial

from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModbusClientManager:
    """Manager do obsługi połączeń Modbus"""
    
    def __init__(self):
        self.client = None
        self.connection_type = 'tcp'
        self.unit_id = 1
        self.is_connected = False
    
    def connect(self, host='192.168.1.100', port=502, connection_type='tcp', 
                timeout=5, unit_id=1, serial_port='COM3', baud_rate=9600):
        """
        Nawiąż połączenie z urządzeniem Modbus
        
        Args:
            host: Adres IP urządzenia (dla TCP)
            port: Port (dla TCP)
            connection_type: 'tcp' lub 'serial'
            timeout: Timeout połączenia w sekundach
            unit_id: ID urządzenia (1-247)
            serial_port: Port serialny (COM3, /dev/ttyUSB0)
            baud_rate: Prędkość transmisji (9600, 19200, itd.)
        
        Returns:
            bool: True jeśli połączenie udane
        """
        try:
            self.connection_type = connection_type
            self.unit_id = unit_id
            
            if connection_type == 'tcp':
                self.client = ModbusTcpClient(
                    host=host,
                    port=port,
                    timeout=timeout
                )
            else:  # serial
                self.client = ModbusSerialClient(
                    method='rtu',
                    port=serial_port,
                    baudrate=baud_rate,
                    timeout=timeout,
                    stopbits=1,
                    bytesize=8,
                    parity='N'
                )
            
            self.is_connected = self.client.connect()
            
            if self.is_connected:
                logger.info(f"✓ Połączono: {connection_type.upper()} ({host}:{port})")
            else:
                logger.error(f"✗ Błąd połączenia: {connection_type.upper()}")
            
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Błąd w connect(): {str(e)}")
            return False
    
    def disconnect(self):
        """Rozłącz"""
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Rozłączono")
    
    def read_registers(self, address=0, count=1, register_type='holding'):
        """
        Odczytaj rejestry
        
        Args:
            address: Adres startowy
            count: Liczba rejestrów
            register_type: 'holding', 'input', 'coil', 'discrete'
        
        Returns:
            list: Lista wartości lub None w przypadku błędu
        """
        try:
            if not self.is_connected:
                logger.error("Brak połączenia")
                return None
            
            if register_type == 'holding':
                result = self.client.read_holding_registers(
                    address=address,
                    count=count,
                    unit=self.unit_id
                )
            elif register_type == 'input':
                result = self.client.read_input_registers(
                    address=address,
                    count=count,
                    unit=self.unit_id
                )
            elif register_type == 'coil':
                result = self.client.read_coils(
                    address=address,
                    count=count,
                    unit=self.unit_id
                )
            elif register_type == 'discrete':
                result = self.client.read_discrete_inputs(
                    address=address,
                    count=count,
                    unit=self.unit_id
                )
            else:
                logger.error(f"Nieznany typ rejestru: {register_type}")
                return None
            
            if hasattr(result, 'registers'):
                return result.registers
            elif hasattr(result, 'bits'):
                return result.bits
            else:
                logger.error("Brak danych w odpowiedzi")
                return None
                
        except ModbusException as e:
            logger.error(f"Błąd Modbus: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Błąd w read_registers(): {str(e)}")
            return None
    
    def write_register(self, address, value, register_type='holding'):
        """
        Zapisz wartość do rejestru
        
        Args:
            address: Adres rejestru
            value: Wartość do zapisania
            register_type: 'holding' lub 'coil'
        
        Returns:
            bool: True jeśli zapis udany
        """
        try:
            if not self.is_connected:
                logger.error("Brak połączenia")
                return False
            
            if register_type == 'holding':
                result = self.client.write_register(
                    address=address,
                    value=value,
                    unit=self.unit_id
                )
            elif register_type == 'coil':
                result = self.client.write_coil(
                    address=address,
                    value=value,
                    unit=self.unit_id
                )
            else:
                logger.error(f"Nieznany typ rejestru: {register_type}")
                return False
            
            return not result.isError()
            
        except Exception as e:
            logger.error(f"Błąd w write_register(): {str(e)}")
            return False