# modbus_client.py - Klient Modbus TCP/Serial

from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException
import logging
import struct

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
    
    @staticmethod
    def u16_to_s16(value):
        """
        Konwertuj U16 (unsigned 16-bit) do S16 (signed 16-bit)
        
        Args:
            value: U16 value (0-65535)
        
        Returns:
            S16 value (-32768 to 32767)
        """
        if value > 32767:
            return value - 65536
        return value
    
    @staticmethod
    def u16_to_f32(high, low):
        """
        Konwertuj dwa U16 rejestry do F32 (IEEE 754 32-bit float)
        
        Args:
            high: Rejestr wysokiej części (adres n)
            low: Rejestr niskiej części (adres n+1)
        
        Returns:
            Float value
        """
        try:
            # Połącz dwa U16 w jedno U32
            u32 = (high << 16) | low
            # Konwertuj U32 do float
            return struct.unpack('>f', struct.pack('>I', u32))[0]
        except:
            return None
    
    def read_registers(self, address=0, count=1, register_type='holding', data_format='s16'):
        """
        Odczytaj rejestry
        
        Args:
            address: Adres startowy
            count: Liczba rejestrów
            register_type: 'holding', 'input', 'coil', 'discrete'
            data_format: Format danych: 's16', 'u16', 'f32', 'f64'
        
        Returns:
            list: Lista wartości lub None w przypadku błędu
        """
        try:
            if not self.is_connected:
                logger.error("Brak połączenia")
                return None
            
            # pymodbus 3.11+ API
            if register_type == 'holding':
                result = self.client.read_holding_registers(
                    address=address,
                    count=count
                )
            elif register_type == 'input':
                result = self.client.read_input_registers(
                    address=address,
                    count=count
                )
            elif register_type == 'coil':
                result = self.client.read_coils(
                    address=address,
                    count=count
                )
            elif register_type == 'discrete':
                result = self.client.read_discrete_inputs(
                    address=address,
                    count=count
                )
            else:
                logger.error(f"Nieznany typ rejestru: {register_type}")
                return None
            
            # Sprawdz czy wyniku jest isError
            if hasattr(result, 'isError') and result.isError():
                logger.error(f"Błąd Modbus: {result}")
                return None
            
            if hasattr(result, 'registers'):
                raw_values = result.registers
                
                # Konwertuj wartości na odpowiedni format
                if data_format == 's16':
                    # Konwertuj U16 do S16 (signed 16-bit)
                    converted = [self.u16_to_s16(v) for v in raw_values]
                    logger.debug(f"Converted to S16: {converted[:10]}...")
                    return converted
                elif data_format == 'u16':
                    return raw_values
                elif data_format == 'f32':
                    # Konwertuj pary U16 do F32
                    if len(raw_values) % 2 != 0:
                        logger.warning("Count musi być parzysty dla F32")
                    converted = []
                    for i in range(0, len(raw_values) - 1, 2):
                        f32_val = self.u16_to_f32(raw_values[i], raw_values[i + 1])
                        converted.append(f32_val)
                    return converted
                else:
                    return raw_values
            elif hasattr(result, 'bits'):
                return result.bits
            else:
                logger.error(f"Brak danych w odpowiedzi: {result}")
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
                    value=value
                )
            elif register_type == 'coil':
                result = self.client.write_coil(
                    address=address,
                    value=value
                )
            else:
                logger.error(f"Nieznany typ rejestru: {register_type}")
                return False
            
            return not result.isError()
            
        except Exception as e:
            logger.error(f"Błąd w write_register(): {str(e)}")
            return False
