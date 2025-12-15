# modbus_logger.py - System logowania do pliku

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime

class ModbusLogger:
    """Manager logowania dla aplikacji Modbus"""
    
    def __init__(self, log_dir='logs', log_level=logging.INFO):
        """
        Inicjalizacja systemu logowania
        
        Args:
            log_dir: Folder na logi
            log_level: Poziom logowania (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Główny logger
        self.logger = logging.getLogger('modbus_monitor')
        self.logger.setLevel(log_level)
        
        # Handler do pliku (rotujący - nowy plik każdego dnia)
        log_file = self.log_dir / f"modbus_monitor_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=7  # Przechowuj 7 ostatnich plików
        )
        file_handler.setLevel(log_level)
        
        # Handler do konsoli
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Dodaj handlery
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_logger(self, name=None):
        """Pobierz logger"""
        if name:
            return logging.getLogger(f'modbus_monitor.{name}')
        return self.logger
    
    def get_logs(self, days=1):
        """Pobierz ostatnie logi"""
        logs = []
        log_files = sorted(self.log_dir.glob('modbus_monitor_*.log'), reverse=True)
        
        for log_file in log_files[:days]:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs.extend(f.readlines())
            except:
                pass
        
        return ''.join(logs[-100:])  # Ostatnie 100 linii
    
    def cleanup_old_logs(self, days=30):
        """Usuń stare logi"""
        import time
        now = time.time()
        
        for log_file in self.log_dir.glob('modbus_monitor_*.log'):
            if os.stat(log_file).st_mtime < now - days * 24 * 3600:
                log_file.unlink()


# Singleton
_logger_instance = None

def get_modbus_logger(log_dir='logs', log_level=logging.INFO):
    """Pobierz instancję loggera"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = ModbusLogger(log_dir, log_level)
    return _logger_instance