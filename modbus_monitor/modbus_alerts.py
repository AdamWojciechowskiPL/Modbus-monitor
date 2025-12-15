# modbus_alerts.py - System alertów i powiadomień

import logging
from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Definicja reguły alertu"""
    signal_name: str
    alert_type: str  # 'threshold_high', 'threshold_low', 'connection_lost', 'anomaly'
    threshold: float = None
    enabled: bool = True
    severity: str = 'warning'  # 'info', 'warning', 'critical'

class AlertsManager:
    """Manager systemu alertów"""
    
    def __init__(self, database=None, notification_callback: Callable = None):
        """
        Inicjalizacja managera alertów
        
        Args:
            database: Instancja ModbusDatabase
            notification_callback: Funkcja do wysyłania powiadomień
        """
        self.database = database
        self.notification_callback = notification_callback
        self.rules: Dict[str, List[AlertRule]] = {}
        self.alert_history: List[Dict] = []
        self.max_history = 1000
    
    def add_rule(self, rule: AlertRule):
        """Dodaj regułę alertu"""
        signal_name = rule.signal_name
        if signal_name not in self.rules:
            self.rules[signal_name] = []
        
        self.rules[signal_name].append(rule)
        logger.info(f"✓ Dodano regułę: {signal_name} - {rule.alert_type}")
    
    def remove_rule(self, signal_name: str, alert_type: str):
        """Usuń regułę alertu"""
        if signal_name in self.rules:
            self.rules[signal_name] = [
                r for r in self.rules[signal_name] 
                if r.alert_type != alert_type
            ]
    
    def check_signal(self, signal_name: str, value: float, status: str = 'ok'):
        """Sprawdź sygnał i wyzwól alerty"""
        if signal_name not in self.rules:
            return
        
        for rule in self.rules[signal_name]:
            if not rule.enabled:
                continue
            
            alert = None
            
            # Sprawdzenie threshold high
            if rule.alert_type == 'threshold_high' and rule.threshold:
                if value > rule.threshold:
                    alert = {
                        'signal_name': signal_name,
                        'alert_type': 'threshold_high',
                        'message': f"Sygnał {signal_name} przekroczył próg: {value} > {rule.threshold}",
                        'severity': rule.severity,
                        'value': value,
                        'timestamp': datetime.now()
                    }
            
            # Sprawdzenie threshold low
            elif rule.alert_type == 'threshold_low' and rule.threshold:
                if value < rule.threshold:
                    alert = {
                        'signal_name': signal_name,
                        'alert_type': 'threshold_low',
                        'message': f"Sygnał {signal_name} poniżej progu: {value} < {rule.threshold}",
                        'severity': rule.severity,
                        'value': value,
                        'timestamp': datetime.now()
                    }
            
            # Sprawdzenie połączenia
            elif rule.alert_type == 'connection_lost' and status == 'error':
                alert = {
                    'signal_name': signal_name,
                    'alert_type': 'connection_lost',
                    'message': f"Utrata połączenia z sygnałem {signal_name}",
                    'severity': rule.severity,
                    'timestamp': datetime.now()
                }
            
            # Jeśli alert wyzwolony
            if alert:
                self.trigger_alert(alert)
    
    def trigger_alert(self, alert: Dict):
        """Wyzwól alert"""
        # Dodaj do historii
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Zapisz do bazy
        if self.database:
            self.database.save_alert(
                signal_name=alert.get('signal_name'),
                alert_type=alert.get('alert_type'),
                message=alert.get('message'),
                severity=alert.get('severity', 'warning')
            )
        
        # Wyślij powiadomienie
        if self.notification_callback:
            self.notification_callback(alert)
        
        # Log
        logger.warning(f"🚨 ALERT: {alert.get('message')}")
    
    def get_active_alerts(self) -> List[Dict]:
        """Pobierz aktywne alerty"""
        return self.alert_history[-10:]  # Ostatnie 10
    
    def clear_alert_history(self):
        """Wyczyść historię alertów"""
        self.alert_history.clear()


class NotificationManager:
    """Manager powiadomień (email, SMS, desktop)"""
    
    def __init__(self):
        self.enabled = True
        self.desktop_notifications = True
        self.email_enabled = False
        self.email_recipients = []
    
    def send_notification(self, alert: Dict):
        """Wyślij powiadomienie"""
        if not self.enabled:
            return
        
        # Desktop notification
        if self.desktop_notifications:
            self.send_desktop_notification(alert)
        
        # Email
        if self.email_enabled and self.email_recipients:
            self.send_email_notification(alert)
    
    def send_desktop_notification(self, alert: Dict):
        """Wyślij powiadomienie na pulpicie"""
        try:
            from plyer import notification
            
            title = f"🚨 {alert.get('severity', 'ALERT').upper()}"
            message = alert.get('message', 'Nieznany alert')
            
            notification.notify(
                title=title,
                message=message,
                timeout=10,
                app_name='Modbus Monitor'
            )
            logger.info(f"✓ Powiadomienie desktop: {message}")
        except ImportError:
            logger.warning("plyer nie zainstalowany (powiadomienia desktop wyłączone)")
        except Exception as e:
            logger.error(f"Błąd powiadomienia: {str(e)}")
    
    def send_email_notification(self, alert: Dict):
        """Wyślij powiadomienie email"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Configurable SMTP settings
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "noreply@modbusmonitor.local"
            
            msg = MIMEMultipart()
            msg['Subject'] = f"[Modbus Alert] {alert.get('signal_name')}"
            msg['From'] = sender_email
            msg['To'] = ', '.join(self.email_recipients)
            
            body = f"""
            Alert Type: {alert.get('alert_type')}
            Signal: {alert.get('signal_name')}
            Message: {alert.get('message')}
            Severity: {alert.get('severity')}
            Time: {alert.get('timestamp')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            logger.info(f"✓ Email alert przygotowany")
        except Exception as e:
            logger.error(f"Błąd email: {str(e)}")