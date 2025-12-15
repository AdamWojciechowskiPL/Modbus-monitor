# DESKTOP_BUILD.md - Budowanie EXE dla Windows

Jak zbudować **standalone aplikację** (.exe) na Windowsie bez konieczności zainstalowanego Pythona.

---

## 📋 Wymagania

### System
- **OS:** Windows 7 lub nowszy
- **RAM:** 4 GB minimum
- **Dysk:** 1 GB wolnego miejsca
- **Python:** 3.8 - 3.12 (zainstalowany)

### Zainstaluj Narzędzia
```bash
pip install pyinstaller
# lub
pip install -e ".[build]"
```

---

## 🚀 Szybki Build (3 kroki)

### Krok 1: Przejdź do Projektu
```bash
cd C:\Users\YourName\modbus-monitor
```

### Krok 2: Uruchom Build Script
```bash
build_exe.bat
```

Lub ręcznie:
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --name=ModbusMonitor
```

### Krok 3: Poczekaj
```
⏳ Building...
📦 Creating executable...
✓ Done! (~2-3 minuty)
```

### Rezultat
```
dist/
└── modbus_monitor_pyqt.exe  ← Twój EXE! (~150 MB)
```

---

## 💻 Uruchamianie EXE

### Podwójny Click
```
dist/modbus_monitor_pyqt.exe
```

### Command Line
```bash
dist\modbus_monitor_pyqt.exe

# lub z argumentami
dist\modbus_monitor_pyqt.exe --debug
```

### Utwórz Shortcut (Opcjonalnie)
```
1. Kliknij prawym przyciskiem: modbus_monitor_pyqt.exe
2. Send to → Desktop (create shortcut)
3. Teraz masz icon na pulpicie
```

---

## 🔧 Zaawansowana Konfiguracja

### build.spec - Plik Konfiguracyjny

Utwórz `build.spec` w głównym katalogu:

```python
# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['modbus_monitor_pyqt.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtCharts',
        'pymodbus',
        'sqlalchemy',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ModbusMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Bez console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ModbusMonitor',
)
```

### Build ze Spec File
```bash
pyinstaller build.spec
```

---

## 📦 Opcje Build'a

### Minimalistyczne (bez console)
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --windowed
```

### Ze Splash Screen
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --windowed ^
    --splash=splash.png
```

### Z Ikoną
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --windowed ^
    --icon=icon.ico
```

### Folder Mode (nie onefile)
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onedir ^
    --windowed
```

### Debug Mode (z console)
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --console  # Pokaże console window
```

---

## 🎨 Dodaj Ikonę

### Utwórz Icon
1. Pobierz ikonę (np. .png lub .jpg)
2. Konwertuj na .ico:
   - Online: https://convertio.co/png-ico/
   - Python:
     ```python
     from PIL import Image
     img = Image.open('icon.png')
     img.save('icon.ico', sizes=[(32,32), (64,64)])
     ```

### Użyj w Build'u
```bash
pyinstaller modbus_monitor_pyqt.py --icon=icon.ico
```

---

## 📚 Wbuduj Pliki (Data Files)

Jeśli aplikacja wymaga dodatkowych plików (.env, templates, etc.):

### Metoda 1: Via Command Line
```bash
pyinstaller modbus_monitor_pyqt.py ^
    --onefile ^
    --add-data ".env:." ^
    --add-data "templates:templates" ^
    --add-data "static:static"
```

### Metoda 2: Via Spec File
```python
datas=[
    ('.env', '.'),
    ('templates', 'templates'),
    ('static', 'static'),
    ('icons', 'icons'),
],
```

---

## 🔍 Troubleshooting Build

### Błąd: "ModuleNotFoundError"
```bash
# Dodaj do hidden imports
pyinstaller modbus_monitor_pyqt.py ^
    --hidden-import=PyQt6 ^
    --hidden-import=pymodbus ^
    --hidden-import=sqlalchemy
```

### Błąd: "Could not find icon"
```bash
# Sprawdź ścieżkę
# Ikona musi być w głównym katalogu lub podaj pełną ścieżkę
pyinstaller modbus_monitor_pyqt.py --icon=C:\path\icon.ico
```

### EXE jest zbyt duży (>200MB)
```bash
# Spróbuj UPX compression (ale wolniej uruchamia się)
pyinstaller modbus_monitor_pyqt.py --upx-dir=C:\UPX

# Lub usuń niepotrzebne moduły
pyinstaller modbus_monitor_pyqt.py --exclude-module=numpy
```

### Aplikacja się nie uruchamia
```bash
1. Otwórz command prompt
2. Uruchom: dist\modbus_monitor_pyqt.exe
3. Czytaj error messages
4. Dodaj missing imports do build'u
```

---

## 🚀 Dystrybucja

### Pakuj do ZIP (dla użytkowników)
```bash
# Skopiuj EXE z zależnościami
xcopy dist\ModbusMonitor modbus-monitor-dist\ /E /I

# Utwórz ZIP
# Prawym przyciskiem: modbus-monitor-dist → Send to → Compressed
```

### Instalator (NSIS) - Opcjonalnie
```bash
pip install pyinstaller-hooks-contrib

# Utwórz setup.nsi plik
# Kompiluj: makensis setup.nsi
# Rezultat: ModbusMonitor-Setup.exe
```

---

## 📝 Kod do Detekcji Runtime vs EXE

Jeśli chcesz inny behavior dla runtime vs EXE:

```python
import sys
import os

# Sprawdź czy biegnie jako EXE
is_frozen = getattr(sys, 'frozen', False)

if is_frozen:
    print("Running as EXE")
    base_path = sys._MEIPASS
else:
    print("Running as Python script")
    base_path = os.path.dirname(os.path.abspath(__file__))

# Użyj base_path do załadowania plików
env_file = os.path.join(base_path, '.env')
```

---

## ✅ Checklist - Przed Release'em

### Testowanie
- [ ] EXE uruchamia się bez błędów
- [ ] Połączenie Modbus działa
- [ ] Alerty się pojawiają
- [ ] Export danych działa
- [ ] Wykresy się rysują
- [ ] Resize okna - UI się zmienia

### Optymalizacja
- [ ] Rozmiar < 200 MB (jeśli możliwe)
- [ ] Startup time < 5 sekund
- [ ] Nie ma memory leaks (czekaj 10 minut)
- [ ] CPU < 5% w idle

### Bezpieczeństwo
- [ ] .env nie zawiera secrets (użyj env variables)
- [ ] Brak hardcoded passwords
- [ ] SSL/TLS dla remote connections
- [ ] Firewall rules skonfigurowane

### Dokumentacja
- [ ] README.md updated
- [ ] QUICK_START.md tested
- [ ] Screenshots added
- [ ] Troubleshooting section filled

---

## 📊 Porównanie: Script vs EXE

| Aspekt | Python Script | EXE |
|--------|---------------|-----|
| Uruchamianie | `python app.py` | Double click |
| Wymagania | Python 3.8+ | Windows 7+ |
| Rozmiar | ~50 MB (code) | ~150 MB (standalone) |
| Prędkość | Wolniejszy start | Szybszy start |
| Użytkownik | Developer | Laik |
| Dystrybucja | GitHub | ZIP file |
| Modyfikacja | Łatwa (kod) | Trudna (zamknięty) |

---

## 🎯 Alternatywne Build Narzędzia

### cx_Freeze
```bash
pip install cx_Freeze
cxfreeze modbus_monitor_pyqt.py
```

### py2exe (Windows only)
```bash
pip install py2exe
python setup.py py2exe
```

### Auto-py-to-exe (GUI dla PyInstaller)
```bash
pip install auto-py-to-exe
auto-py-to-exe
```

---

## 📞 Problemy?

### Nie Mogę Zbudować
```
1. Sprawdź czy Python jest w PATH: python --version
2. Sprawdź czy PyInstaller zainstalowany: pip list | grep pyinstaller
3. Usuń cache: rmdir /s /q build dist *.egg-info
4. Try again: pyinstaller modbus_monitor_pyqt.py --onefile
```

### EXE Się Nie Uruchamia
```
1. Otwórz Command Prompt
2. Uruchom: dist\modbus_monitor_pyqt.exe
3. Czytaj error message
4. Dodaj brakujący import do build'u
5. Rebuild
```

### Brakuje Plików w EXE
```
1. Dodaj do build'u: --add-data "folder:folder"
2. Albo edytuj build.spec
3. Rebuild
```

---

## 🏆 Best Practices

✅ **Zawsze testuj EXE przed dystrybucją**
```bash
dist\modbus_monitor_pyqt.exe
```

✅ **Użyj venv do build'u** (nie global Python)
```bash
python -m venv venv
venv\Scripts\activate
pip install -e ".[all]"
pyinstaller ...
```

✅ **Versjonuj EXE**
```bash
ModbusMonitor-1.0.0.exe
ModbusMonitor-1.1.0.exe
```

✅ **Stwórz Release Notes**
```
v1.0.0 - Initial Release
- WebSocket dashboard
- Desktop application
- Alert system
```

---

## 📚 Więcej Informacji

- **PyInstaller Docs:** https://pyinstaller.readthedocs.io/
- **PyQt6 Docs:** https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Python Packaging:** https://python-packaging.readthedocs.io/

---

## 🎉 Gratulacje!

Twój standalone EXE jest gotowy do dystrybucji! 🚀

Użytkownicy mogą teraz uruchomić aplikację bez zainstalowanego Pythona!

---

Następnie: [README.md](README.md) | [QUICK_START.md](QUICK_START.md)
