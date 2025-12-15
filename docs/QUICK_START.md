# QUICK START - Modbus Monitor (5 minut)

⏱️ **Czas:** 5 minut | 🎯 **Cel:** Uruchumiająca aplikacja z pierwszym połączeniem

---

## 🚀 Krok 1: Przygotowanie (1 minuta)

### Pobierz Projekt
```bash
git clone https://github.com/yourusername/modbus-monitor.git
cd modbus-monitor
```

### Sprawdź Python
```bash
python --version
# ✓ Python 3.8 or higher
```

### Utwórz Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

---

## 📦 Krok 2: Instalacja (2 minuty)

### Zainstaluj Zależności (wybierz JEDNĄ opcję)

**Opcja A: Wszystko (rekomendowane)**
```bash
pip install -e ".[all]"
```

**Opcja B: Tylko Web**
```bash
pip install -e ".[web]"
```

**Opcja C: Tylko Desktop**
```bash
pip install -e ".[desktop]"
```

**Opcja D: Via Requirements File**
```bash
pip install -r requirements.txt
```

⏳ Czekaj 1-2 minuty na instalację...

---

## ⚙️ Krok 3: Konfiguracja (1 minuta)

### Edytuj .env
```bash
# Otwórz plik .env w edytorze
nano .env  # Linux/macOS
# lub
notepad .env  # Windows
```

### Zmień Te Wartości
```env
# Adres urządzenia Modbus
MODBUS_HOST=192.168.1.100

# Port (default 502 dla TCP)
MODBUS_PORT=502

# Zmień na coś bezpiecznego
SECRET_KEY=zmien-to-na-cos-bezpiecznego
```

### Gotowe!
Zapisz plik (Ctrl+S)

---

## ▶️ Krok 4: Uruchomienie (1 minuta)

### Wybierz JEDNĄ opcję:

#### 🌐 WEB APP (Najprostsza)
```bash
python app.py
```
✓ Otwórz: http://localhost:5000

#### 🌐 WEB DASHBOARD (Rekomendowana) ⭐
```bash
python dashboard_app.py
```
✓ Otwórz: http://localhost:5000
- 3 taby: Sygnały, Alerty, Wykresy
- Real-time WebSocket
- Beautiful UI

#### 💻 DESKTOP APP (Dla Windows/Linux/macOS)
```bash
python modbus_monitor_pyqt.py
```
✓ Okno aplikacji się otworzy
- Native GUI
- Dark theme
- Real-time table

---

## 🔌 Krok 5: Pierwsze Połączenie (1 minuta)

### Web App / Dashboard
```
1. Otwórz http://localhost:5000 w przeglądarce
2. Wpisz IP: 192.168.1.100 (lub Twoje)
3. Wpisz Port: 502 (lub Twoje)
4. Kliknij POŁĄCZ (Connect button)
5. Czekaj na "Connected" status 🟢
```

### Desktop App
```
1. Aplikacja się otworzy automatycznie
2. W lewym panelu: Connection Settings
3. Wpisz IP i Port
4. Kliknij "Connect"
5. Czekaj na 🟢 zieloną kropkę
```

---

## ✅ Sukces!

Jeśli widzisz:
- 🟢 Zieloną kropkę = Połączono
- Wartości sygnałów = Czytanie danych
- Aktualizacja co sekundę = Real-time

**Gratulacje! Aplikacja działa! 🎉**

---

## 🧪 Testy - Co Robić Dalej?

### Test 1: Real-time Updates
```
1. Zmień wartość na urządzeniu Modbus
2. Obserwuj aktualizację w aplikacji (<1 sek)
3. ✓ Jeśli się zmienia = OK
```

### Test 2: Alerty (Web Dashboard)
```
1. Przejdź do tab "Alerty"
2. Kliknij "➕ DODAJ REGUŁĘ"
3. Wypełnij:
   - Signal: Sygnał1
   - Type: threshold_high
   - Value: 50.0
   - Severity: critical
4. Kliknij "Add"
5. Zmień wartość > 50 na urządzeniu
6. Alert powinien się pojawić 🚨
```

### Test 3: Eksport (Web Dashboard)
```
1. Zbierz trochę danych (czekaj 10 sekund)
2. Przejdź do tab "Alerty"
3. Kliknij "Eksportuj"
4. Plik CSV zostanie pobrany ✓
```

### Test 4: Wykresy (Web Dashboard)
```
1. Przejdź do tab "Wykresy"
2. Obserwuj dynamiczne aktualizacje
3. Po 20 punktach pojawia się scrolling ✓
```

---

## ⚠️ Problemy?

### Błąd: "Connection refused"
```
1. Sprawdź IP: ping 192.168.1.100
2. Sprawdź port w .env
3. Sprawdź czy urządzenie jest online
4. Sprawdź firewall
```

### Błąd: "ModuleNotFoundError"
```
# Zainstaluj brakujący moduł:
pip install -e ".[all]"
```

### Błąd: "Port 5000 already in use"
```
# Zmień port w .env:
FLASK_PORT=8080

# lub zabij proces:
lsof -i :5000
kill -9 <PID>
```

### Aplikacja desktop się nie otwiera
```
pip install PyQt6 PyQt6-Charts
python modbus_monitor_pyqt.py
```

---

## 📚 Następne Kroki

Po udanym teście:

1. **Przeczytaj README.md** - Pełna dokumentacja
2. **Skonfiguruj Alerty** - ALERTS_GUI_SETUP.md
3. **Zaawansowana Config** - ADVANCED_FEATURES.md
4. **Zbuduj EXE** (opcjonalnie) - DESKTOP_BUILD.md

---

## 🎯 Szybka Referenca - Polecenia

```bash
# Instalacja
pip install -e ".[all]"

# Web app
python app.py

# Web dashboard
python dashboard_app.py

# Desktop app
python modbus_monitor_pyqt.py

# Testy
pytest

# Linting
black .
pylint *.py

# Budowanie EXE
build_exe.bat  # Windows
```

---

## 💡 Tipsy

✅ **Zawsze używaj Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

✅ **Sprawdź Logi**
```bash
tail -f logs/modbus_monitor_*.log  # Linux/macOS
type logs/modbus_monitor_*.log     # Windows
```

✅ **Resetuj Database**
```bash
rm modbus_data.db  # Linux/macOS
del modbus_data.db  # Windows
# Nowy będzie stworzony przy starcie
```

✅ **Zmień Konfigurację**
```bash
# Edytuj .env
MODBUS_HOST=nowy-adres.com
MODBUS_PORT=503
# Restart aplikacji
```

---

## 📞 Potrzebujesz Pomocy?

```
❓ Pytanie      → GitHub Issues
🐛 Bug report   → GitHub Issues + logs
💡 Suggestion   → GitHub Discussions
📧 Email        → your.email@example.com
```

---

## ✨ Gratulacje!

Aplikacja Modbus Monitor jest teraz uruchomiona i gotowa do pracy! 🚀

**Zapraszamy do korzystania!** 🎉

---

Następnie przeczytaj: [README.md](README.md) | [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)
