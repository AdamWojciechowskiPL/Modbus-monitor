# PROJECT_FILES.md - Pełna Struktura Projektu

# 📁 Struktura Plików - Modbus Monitor Complete Edition

## 🎯 Quick Overview

```
modbus-monitor/
├── 📄 PLIKI KONFIGURACYJNE
├── 🐍 MODUŁY PYTHON (8)
├── 🌐 WEB APP (Flask)
├── 💻 DESKTOP APP (PyQt6)
├── 📚 DOKUMENTACJA (7)
└── 🔧 BUILD SCRIPTS
```

---

## 📂 Pełna Struktura Katalogów

```
modbus-monitor/
│
├── 🔧 PLIKI KONFIGURACYJNE
│   ├── requirements.txt                    # Zależności Flask Web
│   ├── requirements_desktop.txt            # Zależności Desktop PyQt6
│   ├── requirements_desktop_extended.txt   # Zależności + Alerts + DB
│   ├── requirements_dashboard.txt          # Zależności WebSocket
│   ├── .env                                # Environment variables
│   ├── .gitignore                          # Git ignore
│   └── setup.py                            # Setup script
│
├── 🐍 CORE MODUŁU PYTHON
│   ├── modbus_client.py                    # Modbus TCP/RTU client
│   ├── data_exporter.py                    # CSV/Excel/JSON export
│   ├── modbus_database.py                  # SQLite/PostgreSQL
│   ├── modbus_alerts.py                    # Alert rules + manager
│   ├── modbus_logger.py                    # File logging (auto-rotate)
│   ├── alerts_gui_widget.py                # PyQt6 Alert GUI
│   ├── modbus_monitor_pyqt.py              # Desktop application
│   └── dashboard_app.py                    # Flask WebSocket backend
│
├── 🌐 WEB APPLICATION
│   ├── app.py                              # Original Flask app (simple)
│   ├── templates/
│   │   ├── index.html                      # Simple Web UI (original)
│   │   ├── dashboard.html                  # Modern Dashboard UI (NOWY)
│   │   └── base.html                       # Base template (optional)
│   ├── static/
│   │   ├── dashboard.js                    # WebSocket client logic
│   │   ├── style.css                       # Custom CSS (optional)
│   │   └── assets/
│   │       └── images/                     # Logo, icons
│   └── config.py                           # Flask config
│
├── 💻 DESKTOP APPLICATION
│   ├── modbus_monitor_pyqt.py              # Main desktop app
│   ├── alerts_gui_widget.py                # Alert management UI
│   ├── build_exe.bat                       # Windows build script
│   ├── build_exe.ps1                       # PowerShell build script
│   ├── build.spec                          # PyInstaller spec file
│   └── resources/
│       └── icons/                          # Application icons
│
├── 📊 BAZA DANYCH
│   └── modbus_data.db                      # SQLite database (auto-created)
│
├── 📝 LOGI
│   └── logs/
│       └── modbus_monitor_YYYYMMDD.log     # Daily log files (auto-created)
│
├── 📤 EKSPORTED DATA
│   └── exports/
│       ├── signals_*.csv                   # Signal exports
│       ├── alerts_*.csv                    # Alert exports
│       ├── data_*.xlsx                     # Excel exports
│       └── data_*.json                     # JSON exports
│
└── 📚 DOKUMENTACJA
    ├── README.md                           # Main readme
    ├── QUICK_START.md                      # 5-minute quick start
    ├── DESKTOP_BUILD.md                    # PyQt6 build instructions
    ├── ADVANCED_FEATURES.md                # Advanced features guide
    ├── FEATURES_CHECKLIST.md               # Complete features list (70+)
    ├── ALERTS_GUI_SETUP.md                 # Alert GUI integration
    ├── DASHBOARD_SETUP.md                  # WebSocket dashboard setup
    └── PROJECT_FILES.md                    # Ten plik!
```

---

## 📋 Szczegółowy Opis Każdego Pliku

### 🔧 PLIKI KONFIGURACYJNE

#### `requirements.txt`
```
Flask==2.3.0
Werkzeug==2.3.0
pymodbus==3.1.0
python-dotenv==1.0.0
```
**Cel:** Minimalne zależności dla Flask Web App
**Rozmiar:** ~50 MB (po instalacji)

#### `requirements_desktop.txt`
```
PyQt6==6.5.0
PyQt6-Qt6==6.5.0
pymodbus==3.1.0
python-dotenv==1.0.0
```
**Cel:** Zależności do desktop aplikacji
**Rozmiar:** ~150 MB

#### `requirements_desktop_extended.txt`
```
PyQt6==6.5.0
PyQt6-Charts==6.5.0
SQLAlchemy==2.0.0
pymodbus==3.1.0
plyer==2.1.0  # Desktop notifications
```
**Cel:** Full desktop app ze wszystkimi features
**Rozmiar:** ~200 MB

#### `requirements_dashboard.txt`
```
Flask==2.3.0
Flask-SocketIO==5.3.0
python-socketio==5.9.0
python-engineio==4.7.1
pymodbus==3.1.0
```
**Cel:** WebSocket dashboard
**Rozmiar:** ~100 MB

#### `.env`
```
MODBUS_HOST=192.168.1.100
MODBUS_PORT=502
DATABASE_URL=sqlite:///modbus_data.db
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```
**Cel:** Zmienne środowiskowe
**Notatka:** Nie pushować do Git!

#### `.gitignore`
```
__pycache__/
*.pyc
*.pyo
.env
modbus_data.db
logs/
exports/
dist/
build/
*.egg-info/
.vscode/
.idea/
venv/
```

#### `setup.py`
```python
from setuptools import setup

setup(
    name='modbus-monitor',
    version='1.0.0',
    packages=['modbus_monitor'],
    ...
)
```
**Cel:** Opakowanie projektu do pip

---

### 🐍 CORE MODUŁY PYTHON

#### `modbus_client.py` (250 linii)
```python
class ModbusClientManager:
    def connect(host, port, type)
    def read_registers(address, count)
    def write_registers(address, values)
    def disconnect()
```
**Funkcje:**
- ✅ Modbus TCP/RTU
- ✅ Connection management
- ✅ Error handling
- ✅ Timeout management

**Używane przez:** Wszystkie aplikacje

#### `data_exporter.py` (200 linii)
```python
class DataExporter:
    def export_csv(signals, filename)
    def export_excel(signals, filename)
    def export_json(signals, filename)
```
**Funkcje:**
- ✅ CSV export
- ✅ Excel (.xlsx)
- ✅ JSON
- ✅ Auto-naming

**Używane przez:** Web, Desktop, Dashboard

#### `modbus_database.py` (300 linii)
```python
class ModbusDatabase:
    def __init__(db_type='sqlite')  # SQLite or PostgreSQL
    def save_signal(signal_name, value)
    def save_alert(signal_name, alert_type, message)
    def get_signal_history(signal_name, minutes)
    def cleanup_old_data(days=30)
```
**Funkcje:**
- ✅ SQLite (default)
- ✅ PostgreSQL (optional)
- ✅ Auto-cleanup
- ✅ Indexed queries

**Tabele:**
- signals (wartości sygnałów)
- alerts (historia alertów)
- events (zdarzenia aplikacji)

**Używane przez:** Desktop, Dashboard

#### `modbus_alerts.py` (250 linii)
```python
class AlertRule:
    signal_name: str
    alert_type: str  # threshold_high, threshold_low, connection_lost, anomaly
    threshold: float
    severity: str    # info, warning, critical
    enabled: bool

class AlertsManager:
    def add_rule(rule)
    def remove_rule(signal_name, alert_type)
    def check_signal(signal_name, value)
    def get_active_alerts()
```
**Funkcje:**
- ✅ 4 typy alertów
- ✅ 3 poziomy ważności
- ✅ Real-time checking
- ✅ Desktop notifications
- ✅ Email notifications

**Używane przez:** Desktop, Dashboard

#### `modbus_logger.py` (150 linii)
```python
class ModbusLogger:
    def setup_logging(log_file, level='INFO')
    def log_info(message)
    def log_error(message)
    def log_alert(alert_data)
```
**Funkcje:**
- ✅ Daily rotation
- ✅ Max 10MB per file
- ✅ Keep 7 recent files
- ✅ Auto-cleanup (30 dni)

**Lokalizacja:** `logs/modbus_monitor_YYYYMMDD.log`

**Używane przez:** Desktop

#### `alerts_gui_widget.py` (400 linii) ⭐ NOWY
```python
class AlertsRuleDialog(QDialog)        # Dialog edycji
class AlertsRulesWidget(QWidget)       # Tabela reguł
class ActiveAlertsWidget(QWidget)      # Active alerts
class AlertsTabWidget(QWidget)         # Combined tab
```
**Funkcje:**
- ✅ Add/edit/delete rules
- ✅ Alert list
- ✅ Real-time update
- ✅ Export to CSV

**Używane przez:** Desktop PyQt6

#### `modbus_monitor_pyqt.py` (600 linii)
```python
class ModbusMonitorApp(QMainWindow):
    def init_ui()
    def setup_styles()
    def connect_modbus()
    def update_signals_table()
    def show_chart()
```
**Funkcje:**
- ✅ PyQt6 UI
- ✅ Real-time table
- ✅ Dark theme
- ✅ Charts (QChart)
- ✅ Alert integration
- ✅ Logging
- ✅ Data export

**Startu:**
```bash
python modbus_monitor_pyqt.py
```

#### `dashboard_app.py` (300 linii) ⭐ NOWY
```python
class ModbusDashboardServer:
    def poll_signals(settings)
    def __websocket_handlers__
    def __rest_api_routes__

@socketio routes:
    /
    /api/status
    /api/alerts
    /api/history/<signal_name>
```
**Funkcje:**
- ✅ Flask + Socket.IO
- ✅ WebSocket real-time
- ✅ Multi-client broadcast
- ✅ REST API
- ✅ Database integration
- ✅ Alert manager

**Start:**
```bash
python dashboard_app.py
# http://localhost:5000
```

---

### 🌐 WEB APPLICATION

#### `app.py` (Original Simple Web App)
```python
@app.route('/')
@app.route('/api/status')
@app.route('/api/export')
```
**Funkcje:**
- ✅ Basic Flask app
- ✅ REST endpoints
- ✅ Simple HTML template
- ✅ Data export

**Start:**
```bash
python app.py
# http://localhost:5000
```

#### `templates/index.html`
```html
<!-- Simple Web UI (original) -->
<form>
    <input type="text" placeholder="Host">
    <input type="number" placeholder="Port">
    <button>Connect</button>
</form>
<table id="signals">
    <!-- Data here -->
</table>
```

#### `templates/dashboard.html` ⭐ NOWY
```html
<!-- Modern WebSocket Dashboard -->
<!-- Bootstrap 5, responsive, 3 tabs -->
<!-- Sygnały, Alerty, Wykresy -->
<!-- 500+ linii HTML + CSS inline -->
```

#### `static/dashboard.js` ⭐ NOWY
```javascript
const socket = io();

socket.on('signals_update', (data) => {
    updateSignalsDisplay(data.signals);
    updateChartsData(data);
});

function connectModbus() { ... }
function addAlertRule() { ... }
function updateChartsData(signals) { ... }
```

**Funkcje:**
- ✅ Socket.IO client
- ✅ Chart.js integration
- ✅ Real-time updates
- ✅ Form handling
- ✅ Notifications

---

### 💻 DESKTOP APPLICATION

#### `modbus_monitor_pyqt.py` (główny plik)
```bash
python modbus_monitor_pyqt.py
```

Tworzy window z:
- Connection panel
- Real-time signals table
- QChart wykresy
- Alert tab (jeśli alerts_gui_widget.py zainstalowany)
- Export buttons

#### `alerts_gui_widget.py` (integracja alertów)
Dodaje tab "Alerty" do aplikacji głównej

#### `build_exe.bat`
```batch
@echo off
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data="templates:templates" ^
    --output=dist

echo Build complete!
```

**Output:** `dist/modbus_monitor_pyqt.exe` (~150 MB)

#### `build_exe.ps1`
```powershell
# PowerShell variant
pyinstaller ... -F
```

#### `build.spec`
```python
# PyInstaller configuration
a = Analysis(['modbus_monitor_pyqt.py'],
    hiddenimports=['PyQt6'],
    datas=[...],
)
```

---

### 📊 BAZA DANYCH

#### `modbus_data.db` (auto-created)
```
SQLite database z tabelami:
├── signals (wartości)
├── alerts (historia)
└── events (zdarzenia)
```

**Rozmiar:** ~1 MB per month
**Auto-cleanup:** 30 dni

---

### 📝 LOGI

#### `logs/modbus_monitor_YYYYMMDD.log`
```
2025-12-15 11:34:22 - modbus_monitor - INFO - ✓ Połączono
2025-12-15 11:34:28 - modbus_monitor - WARNING - 🚨 Alert: Temp > 50°C
2025-12-15 11:35:10 - modbus_monitor - ERROR - Błąd połączenia
```

**Auto-rotate:** Dziennie
**Max size:** 10 MB per file
**Keep:** 7 ostatnich plików

---

### 📤 EKSPORTED DATA

#### `exports/signals_*.csv`
```
timestamp,signal_name,value,unit,status
2025-12-15 11:34:22,Sygnał 1,42.5,°C,ok
2025-12-15 11:34:23,Sygnał 2,100.0,%, ok
```

#### `exports/alerts_*.csv`
```
timestamp,signal_name,alert_type,message,severity
2025-12-15 11:34:28,Temperatura,threshold_high,Temp > 50°C,critical
```

#### `exports/data_*.xlsx`
Formatted Excel z: signals, alerts, events sheets

#### `exports/data_*.json`
```json
{
  "signals": [...],
  "alerts": [...],
  "metadata": {...}
}
```

---

### 📚 DOKUMENTACJA

#### `README.md`
- Ogólny opis
- Features
- Installation
- Quick start

#### `QUICK_START.md`
- 5-minute setup
- First connection
- Basic usage

#### `DESKTOP_BUILD.md`
- PyQt6 installation
- Running desktop app
- Building EXE

#### `ADVANCED_FEATURES.md`
- Database configuration
- Alert setup
- Email notifications
- Logging details

#### `FEATURES_CHECKLIST.md`
- Complete feature list (70+)
- Version comparison
- Architecture details

#### `ALERTS_GUI_SETUP.md`
- Alert GUI integration
- Usage examples
- Testing guide

#### `DASHBOARD_SETUP.md`
- WebSocket setup
- Frontend/backend architecture
- Multi-client support
- Production deployment

---

## 📊 Podsumowanie Liczb

```
PLIKI:
├── Python modules:      8 plików (~2500 linii kodu)
├── Web templates:       3 pliki HTML (~500 linii)
├── JavaScript:          1 plik (~300 linii)
├── Config files:        6 plików
├── Build scripts:       2 pliki
└── Documentation:       7 plików markdown
    RAZEM: ~30 plików

ROZMIARY:
├── Zipped project:      ~2 MB
├── Installed (pip):     ~200-300 MB
├── Standalone EXE:      ~150 MB
└── Database (30 days):  ~50 MB

LINIE KODU:
├── Python:              ~2500 linii
├── HTML/CSS/JS:         ~800 linii
├── Config/Scripts:      ~200 linii
└── Documentation:       ~2000 linii
    RAZEM: ~5500 linii
```

---

## 🚀 Instalacja - Which Files to Get

### OPCJA 1: Tylko Web (Flask)
```
Potrzebujesz:
├── requirements.txt
├── app.py
├── modbus_client.py
├── data_exporter.py
├── templates/
│   └── index.html
└── README.md
```
**Wielkość:** ~50 MB (po pip install)

### OPCJA 2: Desktop Full (PyQt6 + Alerty + DB)
```
Potrzebujesz:
├── requirements_desktop_extended.txt
├── modbus_monitor_pyqt.py
├── alerts_gui_widget.py
├── modbus_client.py
├── modbus_database.py
├── modbus_alerts.py
├── modbus_logger.py
├── data_exporter.py
├── build_exe.bat (do EXE)
└── DESKTOP_BUILD.md
```
**Wielkość:** ~200 MB (po pip install)

### OPCJA 3: Web + WebSocket Dashboard ⭐
```
Potrzebujesz:
├── requirements_dashboard.txt
├── dashboard_app.py
├── modbus_client.py
├── modbus_database.py
├── modbus_alerts.py
├── data_exporter.py
├── templates/
│   └── dashboard.html
├── static/
│   └── dashboard.js
└── DASHBOARD_SETUP.md
```
**Wielkość:** ~100 MB (po pip install)

### OPCJA 4: KOMPLETNY PAKIET (Wszystko) ✨
```
Potrzebujesz: WSZYSTKIE PLIKI
```
**Wielkość:** ~300 MB (po pip install)
**Features:** 70+, wszystkie wersje

---

## 📥 Checklist - Co Mieć

### Minimum (Web)
- [ ] requirements.txt
- [ ] modbus_client.py
- [ ] app.py
- [ ] templates/index.html

### Standard (Desktop)
- [ ] requirements_desktop_extended.txt
- [ ] modbus_monitor_pyqt.py
- [ ] alerts_gui_widget.py
- [ ] modbus_client.py
- [ ] modbus_database.py
- [ ] modbus_alerts.py
- [ ] modbus_logger.py
- [ ] data_exporter.py
- [ ] build_exe.bat (do EXE)

### Premium (Web + Desktop + Dashboard)
- [ ] Wszystkie z powyższych
- [ ] requirements_dashboard.txt
- [ ] dashboard_app.py
- [ ] templates/dashboard.html
- [ ] static/dashboard.js

### Documentation
- [ ] README.md
- [ ] QUICK_START.md
- [ ] DESKTOP_BUILD.md
- [ ] DASHBOARD_SETUP.md

---

## 🎯 Następne Kroki

1. **Pobierz pliki** - wg opcji powyżej
2. **Zainstaluj zależności** - `pip install -r requirements_*.txt`
3. **Uruchom** - `python app.py` lub `python modbus_monitor_pyqt.py`
4. **Testuj** - Podłącz device Modbus
5. **Build EXE** (opcjonalnie) - `build_exe.bat`

---

**Gotowy do pracy! 🚀**