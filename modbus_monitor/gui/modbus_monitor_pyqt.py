# modbus_monitor_pyqt.py - Modern Desktop PyQt6 aplikacja do monitorowania Modbus

import sys
import json
from datetime import datetime
import logging

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QSpinBox,
    QLabel, QComboBox, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
    QStatusBar, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QColor, QFont

# Try to import QtChart - if fails, disable chart features
try:
    from PyQt6.QtChart import QChart, QChartView, QLineSeries
except ImportError:
    pass

# Relative imports from parent package
from ..modbus_client import ModbusClientManager
from ..data_exporter import DataExporter

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModbusMonitorApp(QMainWindow):
    """Główna aplikacja PyQt6 z nowoczesnym designem"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ Modbus Monitor Pro")
        self.setGeometry(50, 50, 1600, 900)
        self.setMinimumSize(1200, 700)
        
        self.modbus_manager = ModbusClientManager()
        self.data_exporter = DataExporter()
        
        self.signals_data = []
        self.connected = False
        self.read_count = 0
        self.error_count = 0
        
        # Polling timer
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.poll_signals)
        self.poll_interval = 1000
        
        self.init_ui()
        self.setup_modern_styles()
    
    def init_ui(self):
        """Zainicjuj nowoczesny interfejs użytkownika"""
        # Centralny widget
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Lewa strona - Konfiguracja (sidebar)
        sidebar = self.create_modern_sidebar()
        main_layout.addWidget(sidebar, 0)
        
        # Separator
        separator = QWidget()
        separator.setFixedWidth(1)
        separator.setStyleSheet("background-color: rgba(100, 200, 220, 0.1);")
        main_layout.addWidget(separator)
        
        # Prawa strona - Główna zawartość
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(16)
        
        # Header
        header = self.create_modern_header()
        right_layout.addLayout(header)
        
        # Tabela sygnałów
        self.signals_table = self.create_modern_table()
        right_layout.addWidget(self.signals_table, 1)
        
        # Przyciski eksportu
        export_layout = self.create_export_buttons()
        right_layout.addLayout(export_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, 1)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(30, 41, 59, 0.5);
                color: #cbd5e1;
                border-top: 1px solid rgba(100, 200, 220, 0.2);
                padding: 8px 12px;
            }
        """)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("✓ Gotowy")
    
    def create_modern_sidebar(self):
        """Utwórz nowoczesny sidebar z konfiguracją"""
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(320)
        sidebar_widget.setStyleSheet("""
            QWidget#sidebar {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
                border-right: 1px solid rgba(100, 200, 220, 0.1);
            }
        """)
        sidebar_widget.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar_widget)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(12)
        
        # Logo
        logo_label = QLabel("⚡ Konfiguracja")
        logo_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        logo_label.setStyleSheet("color: #06b6d4;")
        layout.addWidget(logo_label)
        
        # Separator
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(100, 200, 220, 0.1);")
        layout.addWidget(sep)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        
        # Host/IP
        self.host_input = QLineEdit("192.168.122.38")
        self.host_input.setStyleSheet(self.get_input_style())
        form_layout.addRow(self.create_label("Host/IP"), self.host_input)
        
        # Port
        self.port_input = QSpinBox()
        self.port_input.setValue(5014)
        self.port_input.setMaximum(65535)
        self.port_input.setStyleSheet(self.get_spinbox_style())
        form_layout.addRow(self.create_label("Port"), self.port_input)
        
        # Typ Połączenia
        self.connection_type = QComboBox()
        self.connection_type.addItems(["tcp", "serial"])
        self.connection_type.setStyleSheet(self.get_combo_style())
        form_layout.addRow(self.create_label("Połączenie"), self.connection_type)
        
        layout.addLayout(form_layout)
        
        # Separator
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: rgba(100, 200, 220, 0.1);")
        layout.addWidget(sep2)
        
        # Sygnały
        signals_label = QLabel("⚧ Sygnały")
        signals_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        signals_label.setStyleSheet("color: #8b5cf6;")
        layout.addWidget(signals_label)
        
        signals_form = QFormLayout()
        signals_form.setSpacing(8)
        
        # Liczba Sygnałów
        self.signal_count_input = QSpinBox()
        self.signal_count_input.setValue(48)
        self.signal_count_input.setMaximum(62)
        self.signal_count_input.setStyleSheet(self.get_spinbox_style())
        signals_form.addRow(self.create_label("Liczba"), self.signal_count_input)
        
        # Adres Startowy
        self.start_address_input = QSpinBox()
        self.start_address_input.setValue(0)
        self.start_address_input.setMaximum(65535)
        self.start_address_input.setStyleSheet(self.get_spinbox_style())
        signals_form.addRow(self.create_label("Adres"), self.start_address_input)
        
        # Typ Rejestru
        self.register_type = QComboBox()
        self.register_type.addItems(["holding", "input", "coil", "discrete"])
        self.register_type.setStyleSheet(self.get_combo_style())
        signals_form.addRow(self.create_label("Typ"), self.register_type)
        
        # Format Danych
        self.data_format = QComboBox()
        self.data_format.addItems(["f32", "s16", "u16"])
        self.data_format.setCurrentText("f32")
        self.data_format.setStyleSheet(self.get_combo_style())
        signals_form.addRow(self.create_label("Format"), self.data_format)
        
        # Interwał
        self.interval_input = QSpinBox()
        self.interval_input.setValue(1000)
        self.interval_input.setMinimum(100)
        self.interval_input.setSingleStep(100)
        self.interval_input.setStyleSheet(self.get_spinbox_style())
        signals_form.addRow(self.create_label("Interwał ms"), self.interval_input)
        
        layout.addLayout(signals_form)
        layout.addStretch()
        
        # Separator
        sep3 = QWidget()
        sep3.setFixedHeight(1)
        sep3.setStyleSheet("background-color: rgba(100, 200, 220, 0.1);")
        layout.addWidget(sep3)
        
        # Przycisk połączenia
        self.connect_btn = QPushButton("⚡ Połącz")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setFixedHeight(48)
        self.connect_btn.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.update_connect_button_style()
        layout.addWidget(self.connect_btn)
        
        # Statystyki
        stats_label = QLabel("📄 Statystyki")
        stats_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        stats_label.setStyleSheet("color: #06b6d4;")
        layout.addWidget(stats_label)
        
        # Status
        status_layout = QHBoxLayout()
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #ef4444; font-size: 14px;")
        self.status_label = QLabel("Rozłączony")
        self.status_label.setStyleSheet("color: #f1f5f9; font-weight: bold;")
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        # Odczyty
        reads_layout = QHBoxLayout()
        reads_label = QLabel("Odczytów:")
        reads_label.setStyleSheet("color: #e2e8f0; font-weight: 500;")
        self.read_count_label = QLabel("0")
        self.read_count_label.setStyleSheet("color: #22d3ee; font-weight: bold; font-size: 14px;")
        reads_layout.addWidget(reads_label)
        reads_layout.addStretch()
        reads_layout.addWidget(self.read_count_label)
        layout.addLayout(reads_layout)
        
        # Błędy
        errors_layout = QHBoxLayout()
        errors_label = QLabel("Błędów:")
        errors_label.setStyleSheet("color: #e2e8f0; font-weight: 500;")
        self.error_count_label = QLabel("0")
        self.error_count_label.setStyleSheet("color: #fb7185; font-weight: bold; font-size: 14px;")
        errors_layout.addWidget(errors_label)
        errors_layout.addStretch()
        errors_layout.addWidget(self.error_count_label)
        layout.addLayout(errors_layout)
        
        return sidebar_widget
    
    def update_connect_button_style(self):
        """Zaktualizuj styl przycisku połączenia"""
        if self.connected:
            self.connect_btn.setText("⚧ Rozłącz")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                    color: white;
                    border: 2px solid #991b1b;
                    border-radius: 10px;
                    padding: 12px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
                    border: 2px solid #7f1d1d;
                }
                QPushButton:pressed {
                    background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
                }
            """)
        else:
            self.connect_btn.setText("⚡ Połącz")
            self.connect_btn.setStyleSheet("""
                QPushButton {
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white;
                    border: 2px solid #047857;
                    border-radius: 10px;
                    padding: 12px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
                    border: 2px solid #065f46;
                }
                QPushButton:pressed {
                    background: linear-gradient(135deg, #047857 0%, #065f46 100%);
                }
            """)
    
    def create_modern_header(self):
        """Utwórz nowoczesny nagłówek"""
        layout = QHBoxLayout()
        
        title = QLabel("📡 Monitorowanie sygnałów")
        title.setFont(QFont("Inter", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #f1f5f9;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        return layout
    
    def create_modern_table(self):
        """Utwórz nowoczesną tabelę sygnałów"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "ID", "Adres", "Nazwa", "Wartość", "Jednostka", "Status", "Ostatni Odczyt"
        ])
        
        # Stylowanie tabeli
        table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(15, 23, 42, 0.6);
                alternate-background-color: rgba(30, 41, 59, 0.6);
                gridline-color: rgba(100, 200, 220, 0.1);
                color: #f1f5f9;
                border: 1px solid rgba(100, 200, 220, 0.2);
                border-radius: 10px;
            }
            QHeaderView::section {
                background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)
        
        # Rozmiary kolumn
        header = table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        # Wysokość rzędów
        table.verticalHeader().setDefaultSectionSize(35)
        table.setAlternatingRowColors(True)
        
        return table
    
    def create_export_buttons(self):
        """Utwórz nowoczesne przyciski eksportu"""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # CSV Button - Bright Cyan
        csv_btn = QPushButton("📥 CSV")
        csv_btn.clicked.connect(self.export_csv)
        csv_btn.setMinimumHeight(40)
        csv_btn.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        csv_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
                color: white;
                border: 2px solid #0369a1;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%);
                border: 2px solid #0284c7;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            }
        """)
        layout.addWidget(csv_btn)
        
        # Excel Button - Bright Green
        excel_btn = QPushButton("📥 Excel")
        excel_btn.clicked.connect(self.export_excel)
        excel_btn.setMinimumHeight(40)
        excel_btn.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        excel_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
                color: white;
                border: 2px solid #166534;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                border: 2px solid #15803d;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #15803d 0%, #166534 100%);
            }
        """)
        layout.addWidget(excel_btn)
        
        # JSON Button - Bright Purple
        json_btn = QPushButton("📥 JSON")
        json_btn.clicked.connect(self.export_json)
        json_btn.setMinimumHeight(40)
        json_btn.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        json_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
                color: white;
                border: 2px solid #7c3aed;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #c084fc 0%, #a855f7 100%);
                border: 2px solid #9333ea;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
            }
        """)
        layout.addWidget(json_btn)
        
        # Clear Button - Bright Red/Orange
        clear_btn = QPushButton("🗑️ Wyczyść")
        clear_btn.clicked.connect(self.clear_data)
        clear_btn.setMinimumHeight(40)
        clear_btn.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
                color: white;
                border: 2px solid #c2410c;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #fb923c 0%, #f97316 100%);
                border: 2px solid #ea580c;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
            }
        """)
        layout.addWidget(clear_btn)
        
        return layout
    
    def create_label(self, text):
        """Utwórz sformatowanną etykietę - JASNE KOLORY!"""
        label = QLabel(text)
        label.setStyleSheet("""
            color: #f1f5f9;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.3px;
        """)
        return label
    
    def get_input_style(self):
        return """
            QLineEdit {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(100, 200, 220, 0.3);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 8px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #06b6d4;
                background-color: rgba(30, 41, 59, 0.95);
            }
        """
    
    def get_spinbox_style(self):
        return """
            QSpinBox {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(100, 200, 220, 0.3);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 6px 10px;
                font-size: 12px;
            }
            QSpinBox:focus {
                border: 2px solid #06b6d4;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: rgba(6, 182, 212, 0.2);
                border: none;
            }
        """
    
    def get_combo_style(self):
        return """
            QComboBox {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(100, 200, 220, 0.3);
                border-radius: 8px;
                color: #f1f5f9;
                padding: 6px 10px;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 2px solid #06b6d4;
            }
            QComboBox::drop-down {
                border: none;
                background: rgba(6, 182, 212, 0.1);
            }
            QComboBox QAbstractItemView {
                background-color: rgba(30, 41, 59, 0.9);
                color: #f1f5f9;
                selection-background-color: rgba(6, 182, 212, 0.3);
                border-radius: 6px;
            }
        """
    
    def setup_modern_styles(self):
        """Ustaw nowoczesne style całej aplikacji"""
        self.setStyleSheet("""
            QMainWindow {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
                color: #f1f5f9;
            }
            QStatusBar {
                background-color: rgba(30, 41, 59, 0.5);
                color: #cbd5e1;
                border-top: 1px solid rgba(100, 200, 220, 0.2);
            }
        """)
    
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
                self.update_connect_button_style()
                self.status_label.setText("Połączony")
                self.status_dot.setStyleSheet("color: #22c55e; font-size: 14px;")
                self.statusBar.showMessage(f"✓ Połączono z {host}:{port}")
                
                # Uruchom timer
                self.poll_interval = self.interval_input.value()
                self.poll_timer.start(self.poll_interval)
                logger.info(f"Polling started with interval {self.poll_interval}ms")
            else:
                QMessageBox.critical(self, "Błąd", "Nie udało się połączyć")
        
        except Exception as e:
            logger.error(f"Connect error: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Błąd połączenia: {str(e)}")
    
    def disconnect_modbus(self):
        """Rozłącz z urządzeniem Modbus"""
        try:
            self.poll_timer.stop()
            self.modbus_manager.disconnect()
            self.connected = False
            self.update_connect_button_style()
            self.status_label.setText("Rozłączony")
            self.status_dot.setStyleSheet("color: #ef4444; font-size: 14px;")
            self.statusBar.showMessage("⚧ Rozłączono")
        
        except Exception as e:
            logger.error(f"Disconnect error: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Błąd rozłączenia: {str(e)}")
    
    def poll_signals(self):
        """Odczytaj sygnały (wywoływane przez timer)"""
        try:
            values = self.modbus_manager.read_registers(
                address=self.start_address_input.value(),
                count=self.signal_count_input.value(),
                register_type=self.register_type.currentText().lower(),
                data_format=self.data_format.currentText().lower()
            )
            
            if values is not None:
                signals = []
                for i, value in enumerate(values):
                    # Filtruj -9999 (błędne wartości)
                    is_error = value == -9999.0 or (isinstance(value, (int, float)) and abs(value) > 999999)
                    
                    signals.append({
                        'id': i,
                        'address': self.start_address_input.value() + (i * 2 if self.data_format.currentText() == 'f32' else i),
                        'name': f"Sygnał {i + 1}",
                        'value': f"{value:.2f}" if isinstance(value, float) else str(value),
                        'unit': 'MW' if self.data_format.currentText() == 'f32' else '',
                        'status': 'error' if is_error else 'ok',
                        'lastUpdate': datetime.now().strftime('%H:%M:%S')
                    })
                
                self.update_signals_table(signals)
            else:
                self.error_count += 1
                self.error_count_label.setText(str(self.error_count))
        
        except Exception as e:
            logger.error(f"Poll error: {str(e)}")
            self.error_count += 1
            self.error_count_label.setText(str(self.error_count))
    
    def update_signals_table(self, signals):
        """Zaktualizuj tabelę sygnałów"""
        try:
            self.signals_data = signals
            self.read_count += 1
            self.read_count_label.setText(str(self.read_count))
            
            # Czyść tabelę i dodaj sygnały
            self.signals_table.setRowCount(len(signals))
            
            for row, signal in enumerate(signals):
                # ID
                id_item = QTableWidgetItem(str(signal['id'] + 1))
                id_item.setForeground(QColor("#06b6d4"))
                self.signals_table.setItem(row, 0, id_item)
                
                # Adres
                addr_item = QTableWidgetItem(str(signal['address']))
                addr_item.setForeground(QColor("#94a3b8"))
                self.signals_table.setItem(row, 1, addr_item)
                
                # Nazwa
                name_item = QTableWidgetItem(signal['name'])
                name_item.setForeground(QColor("#cbd5e1"))
                self.signals_table.setItem(row, 2, name_item)
                
                # Wartość
                value_item = QTableWidgetItem(str(signal['value']))
                value_item.setForeground(QColor("#10b981"))
                value_item.setFont(QFont("Courier", 11, QFont.Weight.Bold))
                self.signals_table.setItem(row, 3, value_item)
                
                # Jednostka
                unit_item = QTableWidgetItem(signal['unit'])
                unit_item.setForeground(QColor("#8b5cf6"))
                self.signals_table.setItem(row, 4, unit_item)
                
                # Status
                status_item = QTableWidgetItem(signal['status'].upper())
                if signal['status'] == 'ok':
                    status_item.setForeground(QColor("#22c55e"))
                else:
                    status_item.setForeground(QColor("#ef4444"))
                status_item.setFont(QFont("Inter", 10, QFont.Weight.Bold))
                self.signals_table.setItem(row, 5, status_item)
                
                # Ostatni Odczyt
                time_item = QTableWidgetItem(signal['lastUpdate'])
                time_item.setForeground(QColor("#64748b"))
                self.signals_table.setItem(row, 6, time_item)
        
        except Exception as e:
            logger.error(f"Error in update_signals_table: {str(e)}")
    
    def export_csv(self):
        """Eksportuj do CSV"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako CSV", "", "CSV Files (*.csv)")
            if filename:
                self.data_exporter.export_to_csv(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"✓ Wyeksportowano")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")
    
    def export_excel(self):
        """Eksportuj do Excel"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako Excel", "", "Excel Files (*.xlsx)")
            if filename:
                self.data_exporter.export_to_excel(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"✓ Wyeksportowano")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")
    
    def export_json(self):
        """Eksportuj do JSON"""
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Zapisz jako JSON", "", "JSON Files (*.json)")
            if filename:
                self.data_exporter.export_to_json(self.signals_data, filename)
                QMessageBox.information(self, "Sukces", f"✓ Wyeksportowano")
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
        self.poll_timer.stop()
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
