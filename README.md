# Modbus Monitor - Desktop Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](https://github.com/AdamWojciechowskiPL/Modbus-monitor/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Profesjonalna aplikacja desktopowa do monitorowania urządzeń **Modbus TCP/RTU** z panelem sterowania w czasie rzeczywistym, systemem alertów i eksportem danych.

## 🚀 Status Projektu

**✅ PRODUCTION READY**

| Komponent | Status | Szczegóły |
|-----------|--------|----------|
| **Kod** | ✅ | Native PyQt6 Application |
| **Testy** | ✅ | Unit testy z wysokim pokryciem kodu |
| **Build** | ✅ | Cross-platform (Windows, Linux, macOS) |
| **CI/CD** | ✅ | GitHub Actions (Tests, Quality, Build, Release) |

---

## 🎯 Cechy

### 💻 Desktop Application (PyQt6)
- ✅ Native GUI (Qt)
- ✅ Real-time signals table
- ✅ QChart wykresy
- ✅ Dark theme
- ✅ Connection management
- ✅ Statistics (reads/errors)
- ✅ Export: CSV, Excel, JSON
- ✅ Threading (no UI freeze)

### 🚨 Alert System
- ✅ 4 typy alertów:
  - Threshold High/Low
  - Connection Lost
  - Anomaly Detection
- ✅ 3 poziomy ważności (Info, Warning, Critical)
- ✅ Real-time checking
- ✅ Desktop notifications (Plyer)
- ✅ Email notifications (SMTP)
- ✅ Alert history & rules management
- ✅ GUI alert editor

### 💾 Database & Logging
- ✅ SQLite (default)
- ✅ PostgreSQL (optional)
- ✅ Auto-cleanup (30 days)
- ✅ Indexed queries
- ✅ Daily log rotation

### 📤 Data Export
- ✅ CSV export
- ✅ Excel (.xlsx) support
- ✅ JSON export
- ✅ Auto-filename generation
- ✅ Batch export
- ✅ Timestamp formatting

---

## 📋 Wymagania

### System
- **OS:** Windows 7+, Linux, macOS
- **Python:** 3.8 - 3.12

### Sieć
- Dostęp do urządzenia Modbus (TCP/RTU)
- Internet (opcjonalnie, do email notifications)

---

## 🚀 Quick Installation

### 1. Clone / Pobierz Projekt
```bash
git clone https://github.com/AdamWojciechowskiPL/Modbus-monitor.git
cd modbus-monitor
```

### 2. Zainstaluj Python 3.8+
```bash
python --version
# Python 3.8 or higher
```

### 3. Utwórz Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 4. Zainstaluj Zależności
```bash
# Standardowa instalacja
pip install -r requirements.txt

# Lub z setup.py
pip install -e .
```

### 5. Skonfiguruj .env
```bash
cp .env.example .env

# Edytuj poniższe:
MODBUS_HOST=192.168.1.100
MODBUS_PORT=502
```

### 6. Uruchom Aplikację
```bash
python modbus_monitor_pyqt.py
```

---

## 📁 Struktura Projektu

```
modbus-monitor/
├── 🔧 Configuration
│   ├── requirements.txt
│   ├── setup.py
│   ├── .env.example
│   ├── pytest.ini
│   └── conftest.py
│
├── 🐍 Python Modules
│   ├── modbus_monitor/
│   │   ├── modbus_client.py              # Modbus TCP/RTU
│   │   ├── modbus_database.py            # SQLite/PostgreSQL
│   │   ├── modbus_alerts.py              # Alert system
│   │   ├── modbus_logger.py              # Logging
│   │   ├── data_exporter.py              # Export CSV/Excel/JSON
│   │   └── gui/                          # PyQt6 GUI
│   │
│   └── modbus_monitor_pyqt.py            # Desktop application entry point
│
├── 🧪 Testing
│   ├── tests/
│   │   ├── test_modbus_client.py
│   │   ├── test_modbus_alerts.py
│   │   ├── test_data_exporter.py
│   │   ├── test_modbus_logger.py
│   │   └── README.md
│   └── conftest.py
│
├── 📚 Documentation
│   ├── README.md (ten plik)
│   ├── BUILD.md
│   ├── CHANGELOG.md
│   └── .github/workflows/README.md
│
├── 🔨 Build Scripts
│   ├── setup.bat / setup.sh
│   ├── build_exe.bat / build_exe.sh
│   ├── build.py
│   └── Makefile
│
└── 📁 Auto-created
    ├── modbus_data.db
    ├── logs/
    └── exports/
```

---

## 🎯 Użytkowanie

### Desktop Application (PyQt6)
```bash
python modbus_monitor_pyqt.py
```
**Cechy:**
- Native Qt interface
- Dark theme
- Real-time signals table
- QChart wykresy
- Alert management tab
- Export buttons
- Connection status indicator

---

## 🔌 Modbus Connection

### TCP Configuration
```
Host/IP:        192.168.1.100
Port:           502 (standard)
Unit ID:        1
Start Address:  0
Count:          5 (number of registers)
```

### RTU (Serial) Configuration
```
Port:           COM1 (Windows) lub /dev/ttyUSB0 (Linux)
Baudrate:       9600, 19200, 38400, 115200
Parity:         None, Odd, Even
Stop Bits:      1, 2
```

### Connection Status
- 🟢 Green = Connected & polling
- 🔴 Red = Disconnected or error
- 🟡 Yellow = Connecting...

---

## 🚨 Alerts Configuration

### Email Notifications
```bash
# W .env:
ENABLE_EMAIL=True
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=admin@example.com,operator@example.com
```

---

## 📊 Data Export

### Desktop Application
1. Połącz z Modbus device
2. Zbieraj dane
3. Kliknij "Export" button
4. Wybierz format: CSV, Excel, JSON
5. Plik zostanie zapisany w `exports/`

---

## 🛠️ Build Standalone EXE

### Windows
```bash
build_exe.bat
# Output: dist/modbus_monitor_pyqt.exe (~150-200 MB)
```

### Linux/macOS
```bash
chmod +x build_exe.sh
./build_exe.sh
# Output: dist/modbus_monitor_pyqt (Linux) lub .app (macOS)
```

### Universal (All Platforms)
```bash
python build.py
# lub z czyszczeniem:
python build.py --clean
```

Zobacz [BUILD.md](BUILD.md) dla szczegółowych instrukcji.

---

## 🧪 Testing

### Run All Tests
```bash
pytest
pytest -v
```

### Run with Coverage
```bash
pytest --cov=modbus_monitor --cov-report=html
```

---

## 🐛 Troubleshooting

### Brak Połączenia z Modbus
```
❌ Error: "Connection refused"

✅ Rozwiązanie:
1. Sprawdź IP address
2. Sprawdź port (default: 502)
3. Sprawdź firewall
4. Sprawdź czy device jest online (ping)
5. Sprawdź czy device wspiera Modbus TCP
```

### PyQt6 Issues
```
❌ Error: "No module named 'PyQt6'"

✅ Rozwiązanie:
pip install PyQt6 PyQt6-Charts
# lub
pip install -e ".[desktop]"
```

---

## 📞 Support & Contributing

### Znalazłeś Bug?
1. Otwórz GitHub Issue
2. Opisz problem
3. Załącz logi (logs/modbus_monitor_*.log)

### Chcesz Wnieść Kod?
1. Fork repository
2. Utwórz feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📄 License

MIT License - patrz [LICENSE](LICENSE) file

---

## 🙌 Credits

- **PyQt6** - Desktop GUI
- **pymodbus** - Modbus protocol
- **SQLAlchemy** - ORM database
- **pytest** - Testing framework
