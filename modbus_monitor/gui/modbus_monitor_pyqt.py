# modbus_monitor_pyqt.py - Desktop aplikacja PyQt6 do monitorowania Modbus

import sys
import json
from datetime import datetime
from threading import Thread
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QSpinBox,
    QLabel, QComboBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
    QStatusBar, QHeaderView, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QIcon, QColor, QFont

# Try to import QtChart - if fails, disable chart features
try:
    from PyQt6.QtChart import QChart, QChartView, QLineSeries
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("⚠️  Warning: PyQt6.QtChart not available. Install with: pip install PyQt6-Charts")

from PyQt6.QtCore import QPointF

# Relative imports from parent package
from ..modbus_client import ModbusClientManager
from ..data_exporter import DataExporter

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModbusWorker(QObject):
    """Worker thread do odczytywania sygnałów"""
    
    signals_read = pyqtSignal(list)  # Emituje sygnały po odczytaniu
    error_occurred = pyqtSignal(str)  # Emituje błędy
    
    def __init__(self, modbus_manager):
        super().__init__()
        self.modbus_manager = modbus_manager
        self.running = False
        self.settings = {}
    
    def start_polling(self, settings):
        """Rozpocznij polling sygnałów"""
        self.running = True
        self.settings = settings
        
        while self.running:
            try:
                values = self.modbus_manager.read_registers(
                    address=settings['start_address'],
                    count=settings['count'],
                    register_type=settings['register_type']
                )
                
                if values is not None:
                    signals = []
                    for i, value in enumerate(values):
                        signals.append({
                            'id': i,
                            'address': settings['start_address'] + i,
                            'name': f"Sygnał {i + 1}",
                            'value': value,
                            'unit': '',
                            'status': 'ok',
                            'lastUpdate': datetime.now().strftime('%H:%M:%S')
                        })
                    self.signals_read.emit(signals)
                else:
                    self.error_occurred.emit("Błąd odczytu sygnałów")
                
                QThread.msleep(settings.get('interval', 1000))
            
            except Exception as e:
                self.error_occurred.emit(str(e))
    
    def stop_polling(self):
        """Zatrzymaj polling"""
        self.running = False


class ModbusMonitorApp(QMainWindow):
    """Główna aplikacja PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modbus Monitor - Desktop")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyle('Fusion')
        
        self.modbus_manager = ModbusClientManager()
        self.data_exporter = DataExporter()
        
        self.signals_data = []
        self.connected = False
        self.read_count = 0
        self.error_count = 0
        
        self.worker_thread = None
        self.worker = None
        
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
        """Utwórz panel ustawień"""
        group = QGroupBox("Konfiguracja")
        layout = QFormLayout()
        
        # Połączenie
        self.host_input = QLineEdit("localhost")
        self.port_input = QSpinBox()
        self.port_input.setValue(5020)  # Default to test server
        self.port_input.setMaximum(65535)
        
        self.connection_type = QComboBox()
        self.connection_type.addItems(["tcp", "serial"])
        
        layout.addRow("Host/IP:", self.host_input)
        layout.addRow("Port:", self.port_input)
        layout.addRow("Typ Połączenia:", self.connection_type)
        
        # Sygnały
        self.signal_count_input = QSpinBox()
        self.signal_count_input.setValue(5)
        self.signal_count_input.setMaximum(20)
        
        self.start_address_input = QSpinBox()
        self.start_address_input.setValue(0)
        
        self.register_type = QComboBox()
        self.register_type.addItems(["holding", "input", "coil", "discrete"])
        
        self.interval_input = QSpinBox()
        self.interval_input.setValue(1000)
        self.interval_input.setMinimum(100)
        self.interval_input.setSingleStep(100)
        
        layout.addRow("Liczba Sygnałów:", self.signal_count_input)
        layout.addRow("Adres Startowy:", self.start_address_input)
        layout.addRow("Typ Rejestru:", self.register_type)
        layout.addRow("Interwał (ms):", self.interval_input)
        
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
        layout.addRow("Odczytów:", self.read_count_label)
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
        """Przełącz połączenie"""
        if self.connected:
            self.disconnect_modbus()
        else:
            self.connect_modbus()
    
    def connect_modbus(self):
        """Połącz z urządzeniem Modbus"""
        try:
            host = self.host_input.text()
            port = self.port_input.value()
            connection_type = self.connection_type.currentText().lower()
            
            success = self.modbus_manager.connect(
                host=host,
                port=port,
                connection_type=connection_type,
                timeout=5,
                unit_id=1
            )
            
            if success:
                self.connected = True
                self.connect_btn.setText("Rozłącz")
                self.connect_btn.setStyleSheet("background-color: #ef4444; color: white; font-weight: bold;")
                self.status_label.setText("Połączony")
                self.status_label.setStyleSheet("color: #22c55e;")
                self.statusBar.showMessage(f"Połączono z {host}:{port}")
                
                # Uruchom worker thread
                self.start_polling()
            else:
                QMessageBox.critical(self, "Błąd", "Nie udało się połączyć")
        
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd połączenia: {str(e)}")
    
    def disconnect_modbus(self):
        """Rozłącz z urządzeniem Modbus"""
        try:
            if self.worker:
                self.worker.stop_polling()
            
            if self.worker_thread:
                self.worker_thread.quit()
                self.worker_thread.wait()
            
            self.modbus_manager.disconnect()
            self.connected = False
            self.connect_btn.setText("Połącz")
            self.connect_btn.setStyleSheet("background-color: #22c55e; color: white; font-weight: bold;")
            self.status_label.setText("Rozłączony")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.statusBar.showMessage("Rozłączono")
        
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd rozłączenia: {str(e)}")
    
    def start_polling(self):
        """Rozpocznij polling sygnałów"""
        self.worker_thread = QThread()
        self.worker = ModbusWorker(self.modbus_manager)
        self.worker.moveToThread(self.worker_thread)
        
        settings = {
            'start_address': self.start_address_input.value(),
            'count': self.signal_count_input.value(),
            'register_type': self.register_type.currentText().lower(),
            'interval': self.interval_input.value()
        }
        
        self.worker_thread.started.connect(lambda: self.worker.start_polling(settings))
        self.worker.signals_read.connect(self.update_signals_table)
        self.worker.error_occurred.connect(self.handle_error)
        
        self.worker_thread.start()
    
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
        reply = QMessageBox.question(self, "Potwierdzenie", "Na pewno wyczyścić wszystkie dane?")
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
            self.disconnect_modbus()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = ModbusMonitorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
