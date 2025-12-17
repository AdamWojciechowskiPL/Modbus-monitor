@echo off
REM =============================================================================
REM run.bat - Quick launcher for Modbus Monitor (Windows)
REM =============================================================================
REM
REM This script launches the Modbus Monitor desktop application using the
REM system Python installation.
REM
REM Usage:
REM   run.bat              - Launch normally
REM   run.bat --help       - Show Python help
REM   run.bat --version    - Show Python version
REM
REM Requirements:
REM   - Python 3.8+ in PATH
REM   - Dependencies installed: pip install -r requirements.txt
REM =============================================================================

setlocal enabledelayedexpansion

REM Set colors
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] Python not found in PATH!
    echo.
    echo Please install Python 3.8+ or add it to PATH:
    echo   https://www.python.org/downloads/
    echo.
    echo After installation, run: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i

REM Print header
color 0B
echo.
echo ============================================================================
echo.
echo   ^7Modbus Monitor - Desktop Application Launcher
 echo.
echo ============================================================================
echo.
echo   %PYTHON_VERSION%
echo   Working directory: %cd%
echo.
echo   Starting application...
echo.
echo ============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if modbus_monitor_pyqt.py exists
if not exist "modbus_monitor_pyqt.py" (
    color 0C
    echo [ERROR] modbus_monitor_pyqt.py not found in %cd%
    echo.
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [WARNING] Dependencies not found!
    echo.
    echo Installing dependencies... This may take a few minutes.
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo [ERROR] Failed to install dependencies!
        echo.
        pause
        exit /b 1
    )
)

REM Launch application
color 0A
python modbus_monitor_pyqt.py %*

REM Capture exit code
set EXITCODE=%errorlevel%

if %EXITCODE% equ 0 (
    color 0A
    echo.
    echo Application closed successfully.
    echo.
) else (
    color 0C
    echo.
    echo Application error (exit code: %EXITCODE%)
    echo.
    pause
)

exit /b %EXITCODE%
