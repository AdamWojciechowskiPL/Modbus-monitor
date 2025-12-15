@echo off
REM build_exe.bat - Build standalone Windows EXE with PyInstaller
REM 
REM This script builds a standalone modbus_monitor_pyqt.exe for Windows
REM Installation requires PyInstaller, see DESKTOP_BUILD.md for details
REM 
REM Usage:
 REM   build_exe.bat
REM 
REM Output: dist/modbus_monitor_pyqt.exe (~150-200 MB)

echo.
echo ================================================================
echo  Modbus Monitor - PyInstaller EXE Builder for Windows
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/6] Checking Python version...
python --version
echo.

REM Check if virtual environment exists
if exist "venv" (
    echo [2/6] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [2/6] Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [2/6] Virtual environment created and activated
)
echo.

echo [3/6] Installing dependencies...
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller
echo.

echo [4/6] Checking PyInstaller installation...
pyinstaller --version
echo.

echo [5/6] Building EXE with PyInstaller...
echo This may take 2-5 minutes...
echo.

REM Remove old build/dist directories
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build EXE
pyinstaller --name="modbus_monitor_pyqt" ^
    --onefile ^
    --windowed ^
    --icon=modbus_icon.ico ^
    --add-data="modbus_monitor/gui:modbus_monitor/gui" ^
    --add-data="modbus_monitor/web:modbus_monitor/web" ^
    --add-data=".env.example:." ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtCharts ^
    --hidden-import=pymodbus ^
    --hidden-import=sqlalchemy ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --noconfirm ^
    modbus_monitor_pyqt.py

if errorlevel 1 (
    echo.
    echo [ERROR] PyInstaller build failed!
    echo.
    echo Troubleshooting:
    echo - Check that all dependencies are installed
    echo - Verify modbus_icon.ico exists (optional)
    echo - Try: pip install --upgrade pyinstaller
    pause
    exit /b 1
)

echo.
echo [6/6] Build complete!
echo.
echo ================================================================
echo  Build Summary
echo ================================================================
echo.
echo Output: dist\modbus_monitor_pyqt.exe
echo Size: ~150-200 MB (check with: dir dist\modbus_monitor_pyqt.exe)
echo.
echo To run the application:
echo   1. Double-click dist\modbus_monitor_pyqt.exe
echo   2. Or from command line: dist\modbus_monitor_pyqt.exe
echo.
echo To distribute:
echo   1. Copy dist\modbus_monitor_pyqt.exe to target machine
echo   2. Run on Windows 7+
  echo   3. No Python installation required!
echo.
echo ================================================================
echo.
pause
