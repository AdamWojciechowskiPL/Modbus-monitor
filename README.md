# Modbus Monitor - Complete Edition

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3-green.svg)](https://flask.palletsprojects.com/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6-orange.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![Tests](https://img.shields.io/badge/tests-98%20passing-brightgreen.svg)](https://github.com/AdamWojciechowskiPL/Modbus-monitor/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25+-blue.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Profesjonalna aplikacja do monitorowania urządzeń **Modbus TCP/RTU** z panelem sterowania w czasie rzeczywistym, systemem alertów, eksportem danych i dashboardem webowym.

## 🚀 Status Projektu

**✅ PRODUCTION READY** - Wszystkie testy przychodzą, CI/CD w pełni automatyzowany, dokumentacja kompletna.

| Komponent | Status | Szczegóły |
|-----------|--------|----------|
| **Kod** | ✅ | 3 entry points (app.py, dashboard_app.py, modbus_monitor_pyqt.py) |
| **Testy** | ✅ | 98 unit testów z 85%+ pokryciem kodu |
| **Build** | ✅ | Cross-platform (Windows, Linux, macOS) |
| **CI/CD** | ✅ | GitHub Actions (Tests, Quality, Build, Release) |
| **Dokumentacja** | ✅ | Kompletna dokumentacja techniczna |
| **Zależności** | ✅ | Zablokowany PyQt6-Charts problem |

---

## 🎯 Cechy

### ✨ 70+ Funkcji

#### 🌐 Web Application
- ✅ Flask REST API
- ✅ Real-time WebSocket (Socket.IO)
- ✅ Nowoczesny responsive dashboard
- ✅ 3 taby: Sygnały, Alerty, Wykresy
- ✅ Chart.js wykresy (liniowe + doughnut)
- ✅ Multi-client broadcast
- ✅ Toast notifications
- ✅ Eksport alertów do CSV

#### 💻 Desktop Application (PyQt6)
- ✅ Native GUI (Qt)
- ✅ Real-time signals table
- ✅ QChart wykresy (last 500 points)
- ✅ Dark theme
- ✅ Connection management
- ✅ Statistics (reads/errors)
- ✅ Export: CSV, Excel, JSON
- ✅ Threading (no UI freeze)

#### 🚨 Alert System
- ✅ 4 typy alertów:
  - Threshold High/Low
  - Connection Lost
  - Anomaly Detection
- ✅ 3 poziomy ważności (Info, Warning, Critical)
- ✅ Real-time checking
- ✅ Desktop notifications (Plyer)
- ✅ Email notifications (SMTP)
- ✅ Alert history & rules management
- ✅ GUI alert editor (PyQt6)

#### 💾 Database & Logging
- ✅ SQLite (default)
- ✅ PostgreSQL (optional)
- ✅ Auto-cleanup (30 days)
- ✅ Indexed queries
- ✅ Daily log rotation
- ✅ Max 10MB per file
- ✅ Keep 7 recent files

#### 📤 Data Export
- ✅ CSV export
- ✅ Excel (.xlsx) support
- ✅ JSON export
- ✅ Auto-filename generation
- ✅ Batch export
- ✅ Timestamp formatting

#### 🔧 Configuration
- ✅ Environment variables (.env)
- ✅ 50+ settings
- ✅ CORS support
- ✅ SSL/TLS ready
- ✅ Multi-user support

#### 🛠️ Development & Testing
- ✅ 98 unit tests (pytest)
- ✅ 85%+ code coverage
- ✅ Code quality tools (black, pylint, flake8, mypy, isort)
- ✅ Standalone EXE builder
- ✅ PyInstaller integration
- ✅ Professional packaging (setuptools)

---

## 📋 Wymagania

### System
- **OS:** Windows 7+, Linux, macOS
- **Python:** 3.8 - 3.12
- **Rozmiar:** 300-400 MB (po instalacji)

### Sieć
- Dostęp do urządzenia Modbus (TCP/RTU)
- Port 5000 dostępny (dla web app)
- Internet (opcjonalnie, do email notifications)

### Hardware (opcjonalnie)
- 2GB RAM minimum
- 1GB disk space minimum

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
FLASK_SECRET_KEY=change-this-in-production
```

### 6. Uruchom Aplikację
```bash
# WEB APP - WebSocket Dashboard (REKOMENDOWANE)
python dashboard_app.py
# http://localhost:5000

# lub Simple Flask App
python app.py
# http://localhost:5000

# lub DESKTOP APP
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
│   │   └── alerts_gui_widget.py          # PyQt6 Alert UI
│   │
│   ├── app.py                            # Simple Flask app
│   ├── dashboard_app.py                  # Flask WebSocket backend
│   └── modbus_monitor_pyqt.py            # Desktop application
│
├── 🌐 Web Application
│   ├── templates/
│   │   ├── index.html
│   │   └── dashboard.html
│   └── static/
│       └── dashboard.js
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

## 🎯 Użytkowanie - Szybki Przewodnik

### Web Application - WebSocket Dashboard ⭐ REKOMENDOWANY
```bash
python dashboard_app.py
```
**Cechy:**
- Bootstrap 5 responsive UI
- 3 taby: Sygnały, Alerty, Wykresy
- Real-time WebSocket updates (<50ms)
- Multi-client support
- Dark theme ready
- Chart.js wykresy
- Alert management GUI

**URL:** http://localhost:5000

### Web Application - Simple Flask
```bash
python app.py
```
**Cechy:**
- Simple form interface
- Real-time data table
- REST API endpoints
- Auto-connect/disconnect

**URL:** http://localhost:5000

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

### Tworzenie Reguły Alertu (Web Dashboard)
1. Przejdź do tab "Alerty"
2. Wpisz:
   - **Signal:** Nazwa sygnału
   - **Type:** Typ alertu (threshold_high, threshold_low, etc.)
   - **Threshold:** Wartość progowa
   - **Severity:** Ważność (info, warning, critical)
3. Kliknij "➕ DODAJ REGUŁĘ"

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

### Web Interface
1. Przejdź do tab "Alerty"
2. Kliknij "Eksportuj" (CSV)
3. Plik zostanie pobrany

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

### Test Results
- **Total Tests:** 98
- **Passing:** 98 ✅
- **Coverage:** 85%+
- **Test Time:** ~2-3 minutes

Zobacz [tests/README.md](tests/README.md) dla pełnej dokumentacji testów.

---

## 🔄 CI/CD - GitHub Actions

### Automated Workflows

| Workflow | Trigger | Status |
|----------|---------|--------|
| **Tests** | Push/PR | ✅ Pass (12 matrix jobs) |
| **Code Quality** | Push/PR | ✅ Pass (5 tools) |
| **Build** | Push/Tag | ✅ Pass (3 OS) |
| **Release** | Tag | ✅ Auto-release |

### GitHub Actions Features
- ✅ Multi-Python testing (3.8, 3.9, 3.10, 3.11)
- ✅ Multi-OS testing (Ubuntu, Windows, macOS)
- ✅ Code quality checks (black, pylint, flake8, mypy, isort)
- ✅ Automatic build artifacts
- ✅ Coverage reporting
- ✅ Automatic releases on tags

Zobacz [.github/workflows/README.md](.github/workflows/README.md) dla szczegółów.

---

## 🚀 Production Deployment

### Gunicorn + Nginx (Linux)
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 dashboard_app:app
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "dashboard_app.py"]
```

```bash
docker build -t modbus-monitor .
docker run -p 5000:5000 modbus-monitor
```

### SSL/TLS (HTTPS)
```python
# W dashboard_app.py:
socketio.run(app, ssl_context=('cert.pem', 'key.pem'))
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

### WebSocket Errors
```
❌ Error: "WebSocket connection failed"

✅ Rozwiązanie:
1. Sprawdź port 5000 (localhost:5000)
2. Sprawdź browser console (F12)
3. Sprawdź firewall
4. Restart aplikacji
5. Clear browser cache (Ctrl+Shift+Delete)
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

- **Flask** - Web framework
- **PyQt6** - Desktop GUI
- **pymodbus** - Modbus protocol
- **SQLAlchemy** - ORM database
- **Chart.js** - Web charts
- **Bootstrap 5** - CSS framework
- **pytest** - Testing framework

---

## 📈 Roadmap

### v1.1 (Q1 2025)
- [ ] MQTT integration
- [ ] Advanced filtering
- [ ] User authentication
- [ ] Multi-language support

### v1.2 (Q2 2025)
- [ ] Machine learning alerts
- [ ] Custom report generation
- [ ] Mobile app (React Native)
- [ ] Cloud sync

---

## ❓ FAQ

**P: Czy mogę monitorować wiele urządzeń Modbus jednocześnie?**
A: Aktualnie jedna instancja = jedno urządzenie. Dla wielokrotnych urządzeń uruchom wielokrotne instancje na różnych portach.

**P: Czy dane są zapisywane?**
A: Tak, w SQLite bazie (modbus_data.db). Auto-cleanup po 30 dniach.

**P: Czy mogę eksportować dane historyczne?**
A: Tak, all signals and alerts. CSV, Excel, JSON formaty.

**P: Czy aplikacja wymaga internetu?**
A: Nie, działa 100% offline. Email notifications wymagają internetu.

**P: Czy mogę zmienić UI?**
A: Tak, HTML/CSS w templates/ i static/ są dostępne.

---

## 📊 Performance

```
Typical Performance:
├─ Sygnały:      5-10 sygnałów: ~5 KB/sec
├─ Update rate:  1000 Hz (1 odczyt/ms)
├─ Latency:      <50ms (WebSocket)
├─ Database:     ~1 MB per month
├─ Memory:       ~50-100 MB per instance
└─ CPU:          <5% average
```

---

## 📚 Documentation

| Dokument | Zawartość |
|----------|----------|
| **README.md** | Ogólny opis (ten plik) |
| **BUILD.md** | Build scripts & deployment |
| **CHANGELOG.md** | Version history & changes |
| **tests/README.md** | Unit tests documentation |
| **.github/workflows/README.md** | CI/CD workflows |

---

**Gotowy do monitorowania! 🚀**

Zacznij od [quick installation](#-quick-installation) lub [BUILD.md](BUILD.md) dla szczegółowych instrukcji.
