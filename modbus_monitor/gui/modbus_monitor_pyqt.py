# modbus_monitor_pyqt.py - Desktop aplikacja PyQt6 do monitorowania Modbus

import sys
import json
from datetime import datetime
from threading import Thread
import logging
import socketio

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QSpinBox,
    QLabel, QComboBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
    QStatusBar, QHeaderView, QTabWidget, QProgressBar, QStyle
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QPointF
from PyQt6.QtGui import QIcon, QColor, QFont

# Try to import QtChart - if fails, disable chart features
CHARTS_AVAILABLE = False
try:
    from PyQt6.QtChart import QChart, QChartView, QLineSeries
    CHARTS_AVAILABLE = True
except ImportError:
    # Create dummy classes if QtChart is not available
    class QChart:
        pass
    class QChartView:
        pass
    class QLineSeries:
        pass
    print("\n⚠️  Warning: PyQt6.QtChart not available.")
    print("    Install with: pip install PyQt6-Charts")
    print()

# Relative imports from parent package
from ..data_exporter import DataExporter

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketWorker(QObject):
    """Worker thread do komunikacji z serwerem WebSocket"""
    
    signals_updated = pyqtSignal(list)  # Emituje zaktualizowane sygnały
    connection_status = pyqtSignal(str)  # Połączenie: 'connected', 'disconnected', 'error'
    error_occurred = pyqtSignal(str)    # Błąd
    
    def __init__(self):
        super().__init__()
        self.sio = socketio.Client()
        self.signals_data = []
        self.server_url = None
        self.connected = False
        
        # Rejestruj event handlery
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('signals_update', self.on_signals_update)
        self.sio.on('error', self.on_error)
    
    def connect(self, host, port):
        """Połącz z serwerem WebSocket"""
        try:
            self.server_url = f"http://{host}:{port}"
            logger.info(f"Połączanie z {self.server_url}...")
            self.connection_status.emit('connecting')
            
            self.sio.connect(
                self.server_url,
                transports=['websocket'],
                wait_timeout=10
            )
            return True
        
        except Exception as e:
            error_msg = f"Błąd połączenia: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            self.connection_status.emit('error')
            return False
    
    def disconnect(self):
        """Rozłącz z serwerem"""
        try:
            if self.connected:
                self.sio.disconnect()
                self.connected = False
        except Exception as e:
            logger.error(f"Błąd rozpołączenia: {str(e)}")
    
    def on_connect(self):
        """Handler połączenia"""
        logger.info("✓ Połączono z serwerem")
        self.connected = True
        self.connection_status.emit('connected')
    
    def on_disconnect(self):
        """Handler rozłączenia"""
        logger.info("Rozłączono z serwera")
        self.connected = False
        self.connection_status.emit('disconnected')
    
    def on_signals_update(self, data):
        """Handler aktualizacji sygnałów"""
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            # Konwertuj na format zgodny z GUI
            signals = []
            if isinstance(data, list):
                for i, value in enumerate(data):
                    signals.append({
                        'id': i,
                        'address': i,
                        'name': f"Sygnał {i + 1}",
                        'value': value,
                        'unit': '',
                        'status': 'ok',
                        'lastUpdate': datetime.now().strftime('%H:%M:%S')
                    })
            
            self.signals_data = signals
            self.signals_updated.emit(signals)
        
        except Exception as e:
            logger.error(f"Błąd przetwarzania danych: {str(e)}")
    
    def on_error(self, data):
        """Handler błędu"""
        error_msg = str(data) if data else "Nieznany błąd"
        logger.error(f"Błąd serwera: {error_msg}")
        self.error_occurred.emit(error_msg)


class ModbusMonitorApp(QMainWindow):
    """Główna aplikacja PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Monitor - Desktop")
        self.setGeometry(100, 100, 1200, 700)
        
        # Don't set style - use system default
        # self.setStyle('Fusion') causes error in PyQt6
        
        self.data_exporter = DataExporter()
        
        self.signals_data = []
        self.connected = False
        self.read_count = 0
        self.error_count = 0
        
        self.websocket_thread = None
        self.websocket_worker = None
        
        self.init_ui()
        self.setup_styles()
    
    def init_ui(self):
        """Zainicjuj interfejs użytkownika"""
        # Główny widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Lewa strona - ustawienia
        settings_widget = self.create_settings_panel()
        main_layout.addWidget(settings_widget, 0)
        
        # Prawa strona - tabela i wykresy
        right_layout = QVBoxLayout()
        
        # Nagłówek
        header = self.create_header()
        right_layout.addLayout(header)
        
        # Tabela sygnałów
        self.signals_table = self.create_signals_table()
        right_layout.addWidget(self.signals_table, 1)
        
        # Przyciski eksportu
        export_layout = self.create_export_buttons()
        right_layout.addLayout(export_layout)
        
        main_layout.addLayout(right_layout, 1)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Gotowy")
    
    def create_settings_panel(self):
        """Utwórz panel ustawien"""
        group = QGroupBox("Konfiguracja")
        layout = QFormLayout()
        
        # Połączenie
        self.host_input = QLineEdit("localhost")
        self.port_input = QSpinBox()
        self.port_input.setValue(5020)  # Port serwera WebSocket
        self.port_input.setMaximum(65535)
        
        layout.addRow("Host/IP:", self.host_input)
        layout.addRow("Port (serwer):", self.port_input)
        
        # Przyciski
        self.connect_btn = QPushButton("Połącz")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold;")
        
        layout.addRow(self.connect_btn)
        
        # Statystyki
        layout.addRow("—" * 20, QLabel(""))
        
        self.status_label = QLabel("Rozłączony")
        self.read_count_label = QLabel("0")
        self.error_count_label = QLabel("0")
        
        layout.addRow("Status:", self.status_label)
        layout.addRow("Aktualizacji:", self.read_count_label)
        layout.addRow("Błędów:", self.error_count_label)
        
        group.setLayout(layout)
        widget = QWidget()
        widget_layout = QVBoxLayout(widget)
        widget_layout.addWidget(group)
        widget_layout.addStretch()
        
        return widget
    
    def create_header(self):
        """Utwórz nagłówek"""
        layout = QHBoxLayout()
        
        title = QLabel("Sygnały Modbus")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        return layout
    
    def create_signals_table(self):
        """Utwórz tabelę sygnałów"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Adres", "Nazwa", "Wartość", "Jednostka", "Status", "Ostatni Odczyt"
        ])
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        return table
    
    def create_export_buttons(self):
        """Utwórz przyciski eksportu"""
        layout = QHBoxLayout()
        
        csv_btn = QPushButton("📥 Pobierz CSV")
        csv_btn.clicked.connect(self.export_csv)
        
        excel_btn = QPushButton("📥 Pobierz Excel")
        excel_btn.clicked.connect(self.export_excel)
        
        json_btn = QPushButton("📥 Pobierz JSON")
        json_btn.clicked.connect(self.export_json)
        
        clear_btn = QPushButton("🗑️ Wyczyść")
        clear_btn.clicked.connect(self.clear_data)
        
        layout.addWidget(csv_btn)
        layout.addWidget(excel_btn)
        layout.addWidget(json_btn)
        layout.addWidget(clear_btn)
        
        return layout
    
    def setup_styles(self):
        """Ustaw style aplikacji"""
        dark_stylesheet = """
            QMainWindow {
                background-color: #1f2937;
                color: #e5e7eb;
            }
            QGroupBox {
                border: 1px solid #374151;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #e5e7eb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 4px;
                color: #e5e7eb;
                padding: 5px;
            }
            QPushButton {
                background-color: #0891b2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #06b6d4;
            }
            QTableWidget {
                background-color: #111827;
                alternate-background-color: #1f2937;
                gridline-color: #374151;
                color: #e5e7eb;
            }
            QHeaderView::section {
                background-color: #0891b2;
                color: white;
                padding: 5px;
                border: none;
            }
        """
        self.setStyleSheet(dark_stylesheet)
    
    def toggle_connection(self):
        """Przelaćz połączenie"""
        if self.connected:
            self.disconnect_server()
        else:
            self.connect_server()
    
    def connect_server(self):
        """Połącz z serwerem WebSocket"""
        try:
            host = self.host_input.text()
            port = self.port_input.value()
            
            # Utwórz worker thread
            self.websocket_thread = QThread()
            self.websocket_worker = WebSocketWorker()
            self.websocket_worker.moveToThread(self.websocket_thread)
            
            # Połącz sygnały
            self.websocket_thread.started.connect(lambda: self.websocket_worker.connect(host, port))
            self.websocket_worker.signals_updated.connect(self.update_signals_table)
            self.websocket_worker.connection_status.connect(self.update_connection_status)
            self.websocket_worker.error_occurred.connect(self.handle_error)
            
            # Uruchom wątek
            self.websocket_thread.start()
            self.statusBar.showMessage(f"Połączanie z {host}:{port}...")
        
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd połączenia: {str(e)}")
    
    def disconnect_server(self):
        """Rozłącz z serwerem"""
        try:
            if self.websocket_worker:
                self.websocket_worker.disconnect()
            
            if self.websocket_thread:
                self.websocket_thread.quit()
                self.websocket_thread.wait()
            
            self.connected = False
            self.connect_btn.setText("Połącz")
            self.connect_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold;")
            self.status_label.setText("Rozłączony")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.statusBar.showMessage("Rozłączono")
        
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd rozłączenia: {str(e)}")
    
    def update_connection_status(self, status):
        """Zaktualizuj status połączenia"""
        if status == 'connected':
            self.connected = True
            self.connect_btn.setText("Rozłącz")
            self.connect_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold;")
            self.status_label.setText("Połączony")
            self.status_label.setStyleSheet("color: #22c55e;")
            self.statusBar.showMessage("Połączono z serwerem")
        
        elif status == 'disconnected':
            self.connected = False
            self.connect_btn.setText("Połącz")
            self.connect_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold;")
            self.status_label.setText("Rozłączony")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.statusBar.showMessage("Rozłączono z serwera")
        
        elif status == 'error':
            self.connect_btn.setText("Połącz")
            self.status_label.setText("Błąd")
            self.status_label.setStyleSheet("color: #f59e0b;")
    
    def update_signals_table(self, signals):
        """Zaktualizuj tabelę sygnałów"""
        self.signals_data = signals
        self.read_count += 1
        self.read_count_label.setText(str(self.read_count))
        
        self.signals_table.setRowCount(len(signals))
        
        for row, signal in enumerate(signals):
            self.signals_table.setItem(row, 0, QTableWidgetItem(str(signal['id'] + 1)))
            self.signals_table.setItem(row, 1, QTableWidgetItem(str(signal['address'])))
            self.signals_table.setItem(row, 2, QTableWidgetItem(signal['name']))
            
            value_item = QTableWidgetItem(str(signal['value']))
            value_item.setForeground(QColor("#0891b2"))
            self.signals_table.setItem(row, 3, value_item)
            
            self.signals_table.setItem(row, 4, QTableWidgetItem(signal['unit']))
            
            status_item = QTableWidgetItem(signal['status'].upper())
            if signal['status'] == 'ok':
                status_item.setForeground(QColor("#22c55e"))
            else:
                status_item.setForeground(QColor("#ef4444"))
            self.signals_table.setItem(row, 5, status_item)
            
            self.signals_table.setItem(row, 6, QTableWidgetItem(signal['lastUpdate']))
    
    def handle_error(self, error_msg):
        """Obsłuż błąd"""
        self.error_count += 1
        self.error_count_label.setText(str(self.error_count))
        logger.error(f"Błąd: {error_msg}")
    
    def export_csv(self):
        """Eksportuj do CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako CSV", "", "CSV Files (*.csv)")
            if filename:
                self.data_exporter.export_to_csv(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"Wyeksportowano do {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")
    
    def export_excel(self):
        """Eksportuj do Excel"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako Excel", "", "Excel Files (*.xlsx)")
            if filename:
                self.data_exporter.export_to_excel(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"Wyeksportowano do {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")
    
    def export_json(self):
        """Eksportuj do JSON"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako JSON", "", "JSON Files (*.json)")
            if filename:
                self.data_exporter.export_to_json(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"Wyeksportowano do {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")
    
    def clear_data(self):
        """Wyczyść dane"""
        reply = QMessageBox.question(self, "Potwierdzenie", "Na pewno wyczyść wszystkie dane?")
        if reply == QMessageBox.StandardButton.Yes:
            self.signals_table.setRowCount(0)
            self.signals_data = []
            self.read_count = 0
            self.error_count = 0
            self.read_count_label.setText("0")
            self.error_count_label.setText("0")
    
    def closeEvent(self, event):
        """Obsłuż zamykanie aplikacji"""
        if self.connected:
            self.disconnect_server()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = ModbusMonitorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
