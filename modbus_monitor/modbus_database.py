# modbus_database.py - Obsługa bazy danych (SQLite/PostgreSQL)

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class ModbusDatabase:
    """Manager bazy danych dla przechowywania historii sygnałów"""
    
    def __init__(self, db_type='sqlite', db_path='modbus_data.db', db_url=None):
        """
        Inicjalizacja bazy danych
        
        Args:
            db_type: 'sqlite' lub 'postgresql'
            db_path: Ścieżka do pliku SQLite
            db_url: URL do PostgreSQL (postgresql://user:pass@localhost/dbname)
        """
        self.db_type = db_type
        self.db_path = db_path
        self.db_url = db_url
        self.conn = None
        
        if db_type == 'sqlite':
            self.init_sqlite()
        elif db_type == 'postgresql':
            self.init_postgresql()
    
    def init_sqlite(self):
        """Inicjalizuj SQLite"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.create_tables()
            logger.info(f"✓ SQLite baza danych: {self.db_path}")
        except Exception as e:
            logger.error(f"Błąd SQLite: {str(e)}")
            raise
    
    def init_postgresql(self):
        """Inicjalizuj PostgreSQL"""
        try:
            import psycopg2
            self.conn = psycopg2.connect(self.db_url)
            self.create_tables_pg()
            logger.info("✓ PostgreSQL baza danych połączona")
        except ImportError:
            logger.error("psycopg2 nie zainstalowany. pip install psycopg2-binary")
            raise
        except Exception as e:
            logger.error(f"Błąd PostgreSQL: {str(e)}")
            raise
    
    def create_tables(self):
        """Utwórz tabele SQLite"""
        cursor = self.conn.cursor()
        
        # Tabela sygnałów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_name TEXT NOT NULL,
                signal_address INTEGER,
                value REAL,
                unit TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela alertów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_name TEXT,
                alert_type TEXT,
                message TEXT,
                severity TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela zdarzeń
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indeksy dla wydajności
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signal_timestamp ON signals(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alerts(timestamp)')
        
        self.conn.commit()
    
    def create_tables_pg(self):
        """Utwórz tabele PostgreSQL"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id SERIAL PRIMARY KEY,
                signal_name TEXT NOT NULL,
                signal_address INTEGER,
                value REAL,
                unit TEXT,
                status TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id SERIAL PRIMARY KEY,
                signal_name TEXT,
                alert_type TEXT,
                message TEXT,
                severity TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                event_type TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        self.conn.commit()
    
    def save_signal(self, signal_name: str, value: float, unit: str = '', 
                   status: str = 'ok', address: int = None):
        """Zapisz pomiar sygnału"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    INSERT INTO signals (signal_name, signal_address, value, unit, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (signal_name, address, value, unit, status))
            else:
                cursor.execute('''
                    INSERT INTO signals (signal_name, signal_address, value, unit, status)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (signal_name, address, value, unit, status))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Błąd zapisu sygnału: {str(e)}")
    
    def save_alert(self, signal_name: str, alert_type: str, message: str, 
                  severity: str = 'warning'):
        """Zapisz alert"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    INSERT INTO alerts (signal_name, alert_type, message, severity)
                    VALUES (?, ?, ?, ?)
                ''', (signal_name, alert_type, message, severity))
            else:
                cursor.execute('''
                    INSERT INTO alerts (signal_name, alert_type, message, severity)
                    VALUES (%s, %s, %s, %s)
                ''', (signal_name, alert_type, message, severity))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Błąd zapisu alertu: {str(e)}")
    
    def save_event(self, event_type: str, message: str):
        """Zapisz zdarzenie"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    INSERT INTO events (event_type, message)
                    VALUES (?, ?)
                ''', (event_type, message))
            else:
                cursor.execute('''
                    INSERT INTO events (event_type, message)
                    VALUES (%s, %s)
                ''', (event_type, message))
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Błąd zapisu zdarzenia: {str(e)}")
    
    def get_signal_history(self, signal_name: str, minutes: int = 60) -> List[Dict]:
        """Pobierz historię sygnału za ostatnie N minut"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    SELECT signal_name, value, timestamp
                    FROM signals
                    WHERE signal_name = ? AND timestamp > datetime('now', '-' || ? || ' minutes')
                    ORDER BY timestamp DESC
                    LIMIT 500
                ''', (signal_name, minutes))
            else:
                cursor.execute('''
                    SELECT signal_name, value, timestamp
                    FROM signals
                    WHERE signal_name = %s AND timestamp > NOW() - INTERVAL '%s minutes'
                    ORDER BY timestamp DESC
                    LIMIT 500
                ''', (signal_name, minutes))
            
            rows = cursor.fetchall()
            return [dict(row) for row in reversed(rows)] if rows else []
        except Exception as e:
            logger.error(f"Błąd odczytu historii: {str(e)}")
            return []
    
    def get_alerts(self, hours: int = 24, severity: str = None) -> List[Dict]:
        """Pobierz alerty z ostatnich N godzin"""
        try:
            cursor = self.conn.cursor()
            
            if severity:
                if self.db_type == 'sqlite':
                    cursor.execute('''
                        SELECT * FROM alerts
                        WHERE timestamp > datetime('now', '-' || ? || ' hours')
                        AND severity = ?
                        ORDER BY timestamp DESC
                    ''', (hours, severity))
                else:
                    cursor.execute('''
                        SELECT * FROM alerts
                        WHERE timestamp > NOW() - INTERVAL '%s hours'
                        AND severity = %s
                        ORDER BY timestamp DESC
                    ''', (hours, severity))
            else:
                if self.db_type == 'sqlite':
                    cursor.execute('''
                        SELECT * FROM alerts
                        WHERE timestamp > datetime('now', '-' || ? || ' hours')
                        ORDER BY timestamp DESC
                    ''', (hours,))
                else:
                    cursor.execute('''
                        SELECT * FROM alerts
                        WHERE timestamp > NOW() - INTERVAL '%s hours'
                        ORDER BY timestamp DESC
                    ''', (hours,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"Błąd odczytu alertów: {str(e)}")
            return []
    
    def get_events(self, hours: int = 24) -> List[Dict]:
        """Pobierz zdarzenia z ostatnich N godzin"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    SELECT * FROM events
                    WHERE timestamp > datetime('now', '-' || ? || ' hours')
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (hours,))
            else:
                cursor.execute('''
                    SELECT * FROM events
                    WHERE timestamp > NOW() - INTERVAL '%s hours'
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (hours,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            logger.error(f"Błąd odczytu zdarzeń: {str(e)}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """Usuń stare dane starsze niż N dni"""
        try:
            cursor = self.conn.cursor()
            
            if self.db_type == 'sqlite':
                cursor.execute('''
                    DELETE FROM signals WHERE timestamp < datetime('now', '-' || ? || ' days')
                ''', (days,))
                cursor.execute('''
                    DELETE FROM alerts WHERE timestamp < datetime('now', '-' || ? || ' days')
                ''', (days,))
            else:
                cursor.execute('''
                    DELETE FROM signals WHERE timestamp < NOW() - INTERVAL '%s days'
                ''', (days,))
                cursor.execute('''
                    DELETE FROM alerts WHERE timestamp < NOW() - INTERVAL '%s days'
                ''', (days,))
            
            self.conn.commit()
            logger.info(f"✓ Wyczyszczono dane starsze niż {days} dni")
        except Exception as e:
            logger.error(f"Błąd czyszczenia: {str(e)}")
    
    def close(self):
        """Zamknij połączenie"""
        if self.conn:
            self.conn.close()