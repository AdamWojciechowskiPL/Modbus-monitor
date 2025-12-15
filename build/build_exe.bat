# build_exe.bat - Skrypt budowania EXE na Windows

@echo off
echo ========================================
echo Building Modbus Monitor Desktop App
echo ========================================

REM Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python nie jest zainstalowany!
    pause
    exit /b 1
)

REM Utwórz wirtualne środowisko
echo.
echo [1/4] Tworzenie wirtualnego srodowiska...
python -m venv venv
call venv\Scripts\activate

REM Zainstaluj zależności
echo [2/4] Instalowanie zaleznosciach...
pip install -q -r requirements_desktop.txt

REM Buduj EXE
echo [3/4] Budowanie aplikacji...
pyinstaller --onefile ^
    --windowed ^
    --name "Modbus Monitor" ^
    --icon=icon.ico ^
    --add-data "modbus_client.py:." ^
    --add-data "data_exporter.py:." ^
    modbus_monitor_pyqt.py

REM Przenieś pliki
echo [4/4] Finalizowanie...
if exist "dist" (
    echo.
    echo SUCCESS! Aplikacja zbudowana.
    echo Plik EXE: dist\Modbus Monitor.exe
    echo.
    pause
    start dist
) else (
    echo.
    echo ERROR: Blad podczas budowania!
    pause
    exit /b 1
)