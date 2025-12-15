# ALERTS_GUI_SETUP.md - Integracja GUI Alertów

# 🚨 GUI Zarządzania Alertami - Instrukcja Integracji

## Co Masz

Kompletny widget `alerts_gui_widget.py` z trzema komponentami:

### 1. **AlertsRuleDialog** - Dialog edycji reguł
```
┌─────────────────────────────────────┐
│ Edycja Reguły Alertu                │
├─────────────────────────────────────┤
│ Nazwa Sygnału:    [Temperatura   ]  │
│ Typ Alertu:       [threshold_high]  │
│ Próg Wartości:    [50          ]    │
│ Ważność:          [critical    ]    │
│ Status:           [Włączona    ]    │
│                                     │
│  [Zapisz]  [Anuluj]                 │
└─────────────────────────────────────┘
```

### 2. **AlertsRulesWidget** - Zarządzanie regułami
```
┌─────────────────────────────────────────────────────┐
│ Reguły Alertów                                      │
├──────────┬────────────┬──────┬────────┬─────┬──────┤
│ Sygnał   │ Typ Alertu │ Próg │ Ważność│Stan │Akcje │
├──────────┼────────────┼──────┼────────┼─────┼──────┤
│ Temp     │ threshold… │ 50   │critical│✓    │ID: 0 │
│ Ciśnienie│ threshold… │ 100  │warning │✓    │ID: 1 │
└──────────┴────────────┴──────┴────────┴─────┴──────┘

[➕ Dodaj] [✏️ Edytuj] [🗑️ Usuń] [🔄 Odśwież]
```

### 3. **ActiveAlertsWidget** - Monitoring aktywnych alertów
```
┌──────────────────────────────────────────────────────┐
│ Aktywne Alerty                                       │
├──────────┬──────────┬────────────┬────────┬─────────┤
│ Sygnał   │ Typ      │ Wiadomość  │ Ważn.  │ Czas    │
├──────────┼──────────┼────────────┼────────┼─────────┤
│ Temp     │ thres… h │ Temp > 50°C│critical│11:34:22 │
│ Ciśnienie│ thres… l │ Ciś < 100  │warning │11:35:01 │
└──────────┴──────────┴────────────┴────────┴─────────┘

[🔄 Odśwież] [🗑️ Wyczyść] [💾 Eksportuj]
```

---

## 📦 Instalacja

### Krok 1: Kopiuj plik
```bash
alerts_gui_widget.py → folder projektu
```

### Krok 2: Zmodyfikuj `modbus_monitor_pyqt.py`

Dodaj import na początek:
```python
from alerts_gui_widget import AlertsTabWidget
from modbus_alerts import AlertsManager, AlertRule
from modbus_database import ModbusDatabase
```

### Krok 3: W `ModbusMonitorApp.__init__()`

```python
class ModbusMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # ... istniejący kod ...
        
        # DODAJ:
        self.database = ModbusDatabase(db_type='sqlite')
        self.alerts_manager = AlertsManager(database=self.database)
        
        self.init_ui()
        self.setup_styles()
```

### Krok 4: W `init_ui()` - dodaj tab widget

```python
def init_ui(self):
    # ... istniejący kod ...
    
    # Zastąp pojedynczą tabelę na tab widget:
    self.tab_widget = QTabWidget()
    
    # Tab 1: Sygnały
    signals_widget = QWidget()
    signals_layout = QVBoxLayout(signals_widget)
    self.signals_table = self.create_signals_table()
    signals_layout.addWidget(self.signals_table)
    self.tab_widget.addTab(signals_widget, "📊 Sygnały")
    
    # Tab 2: Alerty
    self.alerts_tab = AlertsTabWidget(self.alerts_manager)
    self.tab_widget.addTab(self.alerts_tab, "🚨 Alerty")
    
    # Dodaj do main layout
    right_layout.addWidget(self.tab_widget, 1)
```

### Krok 5: W `update_signals_table()` - dodaj sprawdzanie alertów

```python
def update_signals_table(self, signals):
    self.signals_data = signals
    self.read_count += 1
    
    # ... istniejący kod tabeli ...
    
    # DODAJ: Sprawdź alerty dla każdego sygnału
    for signal in signals:
        self.alerts_manager.check_signal(
            signal_name=signal['name'],
            value=signal['value'],
            status=signal['status']
        )
    
    # Odśwież tab alertów
    self.alerts_tab.active_widget.refresh_alerts()
```

---

## 🎯 Użytkowanie

### Dodawanie Reguły

1. **Przejdź do Tab "Alerty"**
2. **Kliknij "Reguły Alertów"**
3. **Kliknij "➕ Dodaj Regułę"**
4. **Wypełnij formularz:**
   - Nazwa Sygnału: `Temperatura`
   - Typ Alertu: `threshold_high`
   - Próg: `50`
   - Ważność: `critical`
5. **Kliknij "Zapisz"**

### Edycja Reguły

1. **Wybierz regułę z tabeli**
2. **Kliknij "✏️ Edytuj"**
3. **Zmień parametry**
4. **Kliknij "Zapisz"**

### Usuwanie Reguły

1. **Wybierz regułę**
2. **Kliknij "🗑️ Usuń"**
3. **Potwierdź**

### Monitoring Aktywnych Alertów

1. **Kliknij Tab "Aktywne Alerty"**
2. **Tabela pokazuje alerty w real-time**
3. **Akcje:**
   - 🔄 **Odśwież** - ręczne odświeżenie
   - 🗑️ **Wyczyść** - usunięcie wszystkich z historii
   - 💾 **Eksportuj** - export do CSV

---

## 🎨 Kolory Ważności

| Ważność | Kolor | Oznaczenie |
|---------|-------|-----------|
| `info` | 🟢 Zielony | Informacja |
| `warning` | 🟡 Żółty | Ostrzeżenie |
| `critical` | 🔴 Czerwony | Krytyczne |

---

## 📊 Typy Alertów

```python
# 1. Próg maksymalny
AlertRule('Temperatura', 'threshold_high', 50.0, severity='critical')

# 2. Próg minimalny
AlertRule('Temperatura', 'threshold_low', 10.0, severity='warning')

# 3. Utrata połączenia
AlertRule('Sygnał_1', 'connection_lost', severity='critical')

# 4. Anomalia (advanced)
AlertRule('Ciśnienie', 'anomaly', severity='warning')
```

---

## 💾 Integracja z Bazą Danych

GUI automatycznie integruje się z bazą danych:

```python
# Każdy alert jest zapisywany:
self.database.save_alert(
    signal_name='Temperatura',
    alert_type='threshold_high',
    message='Temperatura > 50°C',
    severity='critical'
)

# Pobierz historię:
alerts = self.database.get_alerts(hours=24)
```

---

## 📧 Powiadomienia Email

### Konfiguracja

```python
from modbus_alerts import NotificationManager

notif_mgr = NotificationManager()
notif_mgr.email_enabled = True
notif_mgr.email_recipients = [
    'admin@example.com',
    'operator@example.com'
]
```

### Integracja z AlertsManager

```python
alerts_manager = AlertsManager(
    database=db,
    notification_callback=notif_mgr.send_notification
)
```

---

## 🖥️ Desktop Notifications

Automatyczne powiadomienia na pulpicie Windows:

```
🚨 CRITICAL
Temperatura przekroczyła próg: 55°C > 50°C
```

Wymaga: `pip install plyer`

---

## 📋 Pełny Przykład Implementacji

```python
# main.py
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout
from modbus_monitor_pyqt import ModbusMonitorApp
from alerts_gui_widget import AlertsTabWidget
from modbus_alerts import AlertsManager, AlertRule
from modbus_database import ModbusDatabase

class EnhancedModbusApp(ModbusMonitorApp):
    def __init__(self):
        super().__init__()
        
        # Inicjalizacja zaawansowanych funkcji
        self.database = ModbusDatabase(db_type='sqlite')
        self.alerts_manager = AlertsManager(database=self.database)
        
        # Dodaj przykładowe reguły
        self.setup_default_alerts()
        
        # Dodaj tab alertów
        self.add_alerts_tab()
    
    def setup_default_alerts(self):
        """Dodaj domyślne reguły alertów"""
        self.alerts_manager.add_rule(
            AlertRule('Sygnał_1', 'threshold_high', 100.0, severity='critical')
        )
        self.alerts_manager.add_rule(
            AlertRule('Sygnał_2', 'threshold_low', 10.0, severity='warning')
        )
    
    def add_alerts_tab(self):
        """Dodaj tab alertów do aplikacji"""
        self.alerts_tab = AlertsTabWidget(self.alerts_manager)
        self.tab_widget.addTab(self.alerts_tab, "🚨 Alerty")

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = EnhancedModbusApp()
    window.show()
    sys.exit(app.exec())
```

---

## 🧪 Testowanie

### Test 1: Dodawanie reguły
```bash
1. Otwórz aplikację
2. Przejdź do Alerty > Reguły Alertów
3. Kliknij Dodaj
4. Wpisz dane
5. Sprawdź czy pojawia się w tabeli
```

### Test 2: Wyzwolenie alertu
```bash
1. Dodaj regułę: Temp > 25
2. Uruchom simulator ze wartością 30
3. Sprawdź czy pojawia się w "Aktywne Alerty"
4. Sprawdź notification na pulpicie
```

### Test 3: Export alertów
```bash
1. Wyzwól kilka alertów
2. Przejdź do "Aktywne Alerty"
3. Kliknij "Eksportuj"
4. Sprawdź plik CSV
```

---

## 🚀 Następne Kroki

1. **Zainstaluj plik**
   ```bash
   cp alerts_gui_widget.py project/
   ```

2. **Zmodyfikuj modbus_monitor_pyqt.py**
   - Dodaj import
   - Inicjalizuj AlertsManager
   - Dodaj AlertsTabWidget

3. **Dodaj domyślne reguły**
   ```python
   alerts_manager.add_rule(AlertRule(...))
   ```

4. **Testuj**
   ```bash
   python modbus_monitor_pyqt.py
   ```

5. **Buduj EXE**
   ```bash
   build_exe.bat
   ```

---

**GUI Alertów gotowe do użytku! 🎉**