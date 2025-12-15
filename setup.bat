@echo off
REM setup.bat - Setup Development Environment for Windows
REM
REM Creates virtual environment and installs all dependencies
REM
REM Usage:
 REM   setup.bat
REM

echo.
echo ================================================================
echo  Modbus Monitor - Development Environment Setup (Windows)
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

echo [1/4] Checking Python version...
python --version
echo.

REM Create virtual environment
if exist "venv" (
    echo [2/4] Virtual environment already exists
) else (
    echo [2/4] Creating virtual environment...
    python -m venv venv
)
echo.

echo [3/4] Activating virtual environment and upgrading pip...
call venv\Scripts\activate.bat
pip install --quiet --upgrade pip setuptools wheel
echo.

echo [4/4] Installing dependencies...
pip install --quiet --upgrade -r requirements.txt
pip install --quiet pytest pytest-cov pytest-mock black pylint flake8 mypy pyinstaller
echo.

echo ================================================================
echo  Setup Complete!
echo ================================================================
echo.
echo Virtual environment created at: venv\
echo.
echo Next steps:
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Run development server:
echo    python app.py                 (Simple Flask)
echo    python dashboard_app.py       (WebSocket dashboard - recommended)
echo    python modbus_monitor_pyqt.py (Desktop GUI)
echo.
echo 3. Run tests:
echo    pytest                        (All tests)
echo    pytest -v                     (Verbose)
echo    pytest --cov=modbus_monitor   (With coverage)
echo.
echo 4. Build executable:
echo    build_exe.bat                 (Build standalone)
echo    python build.py               (Cross-platform build)
echo.
echo 5. Code quality:
echo    black modbus_monitor          (Format code)
echo    pylint modbus_monitor         (Lint)
echo    flake8 modbus_monitor         (Style check)
echo.
echo For more information, see:
echo   - README.md
echo   - docs/QUICK_START.md
echo   - tests/README.md
echo.
echo ================================================================
echo.
pause
