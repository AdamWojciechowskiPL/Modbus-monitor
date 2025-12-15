# alerts_gui_widget.py - GUI do zarządzania alertami

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QSpinBox, QComboBox, QDialog, QFormLayout,
    QLabel, QMessageBox, QTabWidget, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from modbus_alerts import AlertRule, AlertsManager

class AlertsRuleDialog(QDialog):
    """Dialog do edycji reguły alertu"""
    
    def __init__(self, parent=None, rule=None):
        super().__init__(parent)
        self.setWindowTitle("Edycja Reguły Alertu")
        self.setGeometry(200, 200, 400, 300)
        self.rule = rule
        
        layout = QFormLayout()
        
        # Nazwa sygnału
        self.signal_name_input = QLineEdit()
        if rule:
            self.signal_name_input.setText(rule.signal_name)
        layout.addRow("Nazwa Sygnału:", self.signal_name_input)
        
        # Typ alertu
        self.alert_type_combo = QComboBox()
        self.alert_type_combo.addItems([
            'threshold_high',
            'threshold_low',
            'connection_lost',
            'anomaly'
        ])
        if rule:
            self.alert_type_combo.setCurrentText(rule.alert_type)
        layout.addRow("Typ Alertu:", self.alert_type_combo)
        
        # Próg (value)
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(-10000, 10000)
        self.threshold_spinbox.setValue(0)
        if rule and rule.threshold:
            self.threshold_spinbox.setValue(int(rule.threshold))
        layout.addRow("Próg Wartości:", self.threshold_spinbox)
        
        # Ważność
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(['info', 'warning', 'critical'])
        if rule:
            self.severity_combo.setCurrentText(rule.severity)
        layout.addRow("Ważność:", self.severity_combo)
        
        # Włączony
        self.enabled_combo = QComboBox()
        self.enabled_combo.addItems(['Włączona', 'Wyłączona'])
        if rule and not rule.enabled:
            self.enabled_combo.setCurrentIndex(1)
        layout.addRow("Status:", self.enabled_combo)
        
        # Przyciski
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Zapisz")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def get_rule(self):
        """Pobierz regułę z formularza"""
        return AlertRule(
            signal_name=self.signal_name_input.text(),
            alert_type=self.alert_type_combo.currentText(),
            threshold=float(self.threshold_spinbox.value()),
            enabled=(self.enabled_combo.currentIndex() == 0),
            severity=self.severity_combo.currentText()
        )


class AlertsRulesWidget(QWidget):
    """Widget do wyświetlania i zarządzania regułami alertów"""
    
    rule_added = pyqtSignal(AlertRule)
    rule_removed = pyqtSignal(str, str)  # signal_name, alert_type
    
    def __init__(self, alerts_manager: AlertsManager, parent=None):
        super().__init__(parent)
        self.alerts_manager = alerts_manager
        self.init_ui()
    
    def init_ui(self):
        """Inicjalizuj interfejs"""
        layout = QVBoxLayout()
        
        # Nagłówek
        header = QLabel("Reguły Alertów")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Tabela reguł
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels([
            "Sygnał", "Typ Alertu", "Próg", "Ważność", "Status", "Akcje"
        ])
        
        header = self.rules_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        self.refresh_rules_table()
        layout.addWidget(self.rules_table)
        
        # Przyciski
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Dodaj Regułę")
        add_btn.clicked.connect(self.add_rule)
        
        edit_btn = QPushButton("✏️ Edytuj")
        edit_btn.clicked.connect(self.edit_rule)
        
        delete_btn = QPushButton("🗑️ Usuń")
        delete_btn.clicked.connect(self.delete_rule)
        
        refresh_btn = QPushButton("🔄 Odśwież")
        refresh_btn.clicked.connect(self.refresh_rules_table)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def refresh_rules_table(self):
        """Odśwież tabelę reguł"""
        self.rules_table.setRowCount(0)
        
        row = 0
        for signal_name, rules in self.alerts_manager.rules.items():
            for rule in rules:
                self.rules_table.insertRow(row)
                
                # Sygnał
                self.rules_table.setItem(row, 0, QTableWidgetItem(signal_name))
                
                # Typ
                self.rules_table.setItem(row, 1, QTableWidgetItem(rule.alert_type))
                
                # Próg
                threshold_text = str(rule.threshold) if rule.threshold else "N/A"
                self.rules_table.setItem(row, 2, QTableWidgetItem(threshold_text))
                
                # Ważność
                severity_item = QTableWidgetItem(rule.severity)
                if rule.severity == 'critical':
                    severity_item.setForeground(QColor("#ef4444"))
                elif rule.severity == 'warning':
                    severity_item.setForeground(QColor("#f59e0b"))
                else:
                    severity_item.setForeground(QColor("#22c55e"))
                self.rules_table.setItem(row, 3, severity_item)
                
                # Status
                status_text = "✓ Włączona" if rule.enabled else "✗ Wyłączona"
                status_item = QTableWidgetItem(status_text)
                status_item.setForeground(QColor("#22c55e" if rule.enabled else "#ef4444"))
                self.rules_table.setItem(row, 4, status_item)
                
                # Akcje (info)
                action_item = QTableWidgetItem(f"ID: {row}")
                self.rules_table.setItem(row, 5, action_item)
                
                row += 1
    
    def add_rule(self):
        """Dodaj nową regułę"""
        dialog = AlertsRuleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule = dialog.get_rule()
            self.alerts_manager.add_rule(rule)
            self.rule_added.emit(rule)
            self.refresh_rules_table()
            QMessageBox.information(self, "Sukces", f"Reguła dla '{rule.signal_name}' dodana")
    
    def edit_rule(self):
        """Edytuj wybraną regułę"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Błąd", "Wybierz regułę do edycji")
            return
        
        signal_name = self.rules_table.item(current_row, 0).text()
        alert_type = self.rules_table.item(current_row, 1).text()
        
        # Pobierz bieżącą regułę
        if signal_name in self.alerts_manager.rules:
            for rule in self.alerts_manager.rules[signal_name]:
                if rule.alert_type == alert_type:
                    # Usuń starą
                    self.alerts_manager.remove_rule(signal_name, alert_type)
                    
                    # Edytuj
                    dialog = AlertsRuleDialog(self, rule)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        new_rule = dialog.get_rule()
                        self.alerts_manager.add_rule(new_rule)
                        self.refresh_rules_table()
                        QMessageBox.information(self, "Sukces", "Reguła zaktualizowana")
                    break
    
    def delete_rule(self):
        """Usuń wybraną regułę"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Błąd", "Wybierz regułę do usunięcia")
            return
        
        signal_name = self.rules_table.item(current_row, 0).text()
        alert_type = self.rules_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Potwierdzenie",
            f"Usunąć regułę '{signal_name}' - {alert_type}?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.alerts_manager.remove_rule(signal_name, alert_type)
            self.rule_removed.emit(signal_name, alert_type)
            self.refresh_rules_table()
            QMessageBox.information(self, "Sukces", "Reguła usunięta")


class ActiveAlertsWidget(QWidget):
    """Widget do wyświetlania aktywnych alertów"""
    
    def __init__(self, alerts_manager: AlertsManager, parent=None):
        super().__init__(parent)
        self.alerts_manager = alerts_manager
        self.init_ui()
    
    def init_ui(self):
        """Inicjalizuj interfejs"""
        layout = QVBoxLayout()
        
        # Nagłówek
        header = QLabel("Aktywne Alerty")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Tabela alertów
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels([
            "Sygnał", "Typ", "Wiadomość", "Ważność", "Czas"
        ])
        
        header = self.alerts_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.refresh_alerts()
        layout.addWidget(self.alerts_table)
        
        # Przyciski
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Odśwież")
        refresh_btn.clicked.connect(self.refresh_alerts)
        
        clear_btn = QPushButton("🗑️ Wyczyść")
        clear_btn.clicked.connect(self.clear_alerts)
        
        export_btn = QPushButton("💾 Eksportuj")
        export_btn.clicked.connect(self.export_alerts)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def refresh_alerts(self):
        """Odśwież listę aktywnych alertów"""
        self.alerts_table.setRowCount(0)
        
        active_alerts = self.alerts_manager.get_active_alerts()
        
        for row, alert in enumerate(active_alerts):
            self.alerts_table.insertRow(row)
            
            # Sygnał
            self.alerts_table.setItem(row, 0, QTableWidgetItem(alert.get('signal_name', '')))
            
            # Typ
            self.alerts_table.setItem(row, 1, QTableWidgetItem(alert.get('alert_type', '')))
            
            # Wiadomość
            self.alerts_table.setItem(row, 2, QTableWidgetItem(alert.get('message', '')))
            
            # Ważność
            severity = alert.get('severity', 'warning')
            severity_item = QTableWidgetItem(severity)
            if severity == 'critical':
                severity_item.setForeground(QColor("#ef4444"))
                severity_item.setBackground(QColor("#fecaca"))
            elif severity == 'warning':
                severity_item.setForeground(QColor("#d97706"))
                severity_item.setBackground(QColor("#fef3c7"))
            else:
                severity_item.setForeground(QColor("#059669"))
            self.alerts_table.setItem(row, 3, severity_item)
            
            # Czas
            timestamp = alert.get('timestamp')
            time_str = timestamp.strftime('%H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
            self.alerts_table.setItem(row, 4, QTableWidgetItem(time_str))
    
    def clear_alerts(self):
        """Wyczyść historię alertów"""
        reply = QMessageBox.question(
            self,
            "Potwierdzenie",
            "Wyczyścić historię alertów?"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.alerts_manager.clear_alert_history()
            self.refresh_alerts()
            QMessageBox.information(self, "Sukces", "Historia alertów wyczyszczona")
    
    def export_alerts(self):
        """Eksportuj alerty do CSV"""
        try:
            import csv
            from datetime import datetime
            
            filename = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Sygnał', 'Typ', 'Wiadomość', 'Ważność', 'Czas'])
                
                for alert in self.alerts_manager.get_active_alerts():
                    writer.writerow([
                        alert.get('signal_name', ''),
                        alert.get('alert_type', ''),
                        alert.get('message', ''),
                        alert.get('severity', ''),
                        alert.get('timestamp', '')
                    ])
            
            QMessageBox.information(self, "Sukces", f"Alerty wyeksportowane do {filename}")
        
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Błąd eksportu: {str(e)}")


class AlertsTabWidget(QWidget):
    """Główny widget alertów (Reguły + Aktywne)"""
    
    def __init__(self, alerts_manager: AlertsManager, parent=None):
        super().__init__(parent)
        self.alerts_manager = alerts_manager
        self.init_ui()
    
    def init_ui(self):
        """Inicjalizuj interfejs"""
        layout = QVBoxLayout()
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Reguły
        self.rules_widget = AlertsRulesWidget(self.alerts_manager)
        tabs.addTab(self.rules_widget, "📋 Reguły Alertów")
        
        # Tab 2: Aktywne alerty
        self.active_widget = ActiveAlertsWidget(self.alerts_manager)
        tabs.addTab(self.active_widget, "🚨 Aktywne Alerty")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def refresh(self):
        """Odśwież wszystkie widgety"""
        self.rules_widget.refresh_rules_table()
        self.active_widget.refresh_alerts()