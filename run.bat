@echo off
REM =============================================================================
REM run.bat - Quick launcher for Modbus Monitor (Windows with local venv)
REM =============================================================================
REM
REM This script launches the Modbus Monitor desktop application using the
REM local Python installation from the venv directory.
REM
REM If venv doesn't exist, it will be created and dependencies installed.
REM
REM Usage:
REM   run.bat              - Launch normally
REM   run.bat --help       - Show Python help
REM   run.bat --version    - Show Python version
REM
REM Requirements:
REM   - Python 3.8+ installed system-wide (for creating venv)
REM   - Virtual environment will be auto-created if missing
REM =============================================================================

setlocal enabledelayedexpansion

REM Set colors
for /F %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

REM Get script directory
set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set PIP_EXE=%VENV_DIR%\Scripts\pip.exe

REM Print header
color 0B
echo.
echo ============================================================================
echo.
echo   ^7 Modbus Monitor - Desktop Application Launcher
echo.
echo ============================================================================
echo.

REM Check if Python executable exists in venv
if not exist "%PYTHON_EXE%" (
    echo   [INFO] Virtual environment not found. Creating...
    echo.
    
    REM Check system Python
    python --version >nul 2>&1
    if errorlevel 1 (
        color 0C
        echo   [ERROR] System Python not found in PATH!
        echo.
        echo   Please install Python 3.8+ or add it to PATH:
        echo     https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
    
    REM Create venv
    echo   Creating virtual environment in: %VENV_DIR%
    echo.
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        color 0C
        echo   [ERROR] Failed to create virtual environment!
        echo.
        pause
        exit /b 1
    )
    echo   Virtual environment created successfully.
    echo.
)

REM Get Python version
for /f "tokens=*" %%i in ('"%PYTHON_EXE%" --version 2^>^&1') do set PYTHON_VERSION=%%i

echo   %PYTHON_VERSION%
echo   Using: %PYTHON_EXE%
echo   Working directory: %SCRIPT_DIR%
echo.

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Check if modbus_monitor_pyqt.py exists
if not exist "modbus_monitor_pyqt.py" (
    color 0C
    echo   [ERROR] modbus_monitor_pyqt.py not found in %SCRIPT_DIR%
    echo.
    pause
    exit /b 1
)

REM Check if PyQt6 is installed
"%PYTHON_EXE%" -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo   [INFO] Installing dependencies in venv...
    echo.
    "%PIP_EXE%" install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo   [ERROR] Failed to install dependencies!
        echo.
        pause
        exit /b 1
    )
    echo.
)

echo   Starting application...
echo.
echo ============================================================================
echo.

REM Launch application with venv Python
color 0A
"%PYTHON_EXE%" modbus_monitor_pyqt.py %*

REM Capture exit code
set EXITCODE=%errorlevel%

color 0B
echo.
if %EXITCODE% equ 0 (
    echo   [OK] Application closed successfully.
) else (
    color 0C
    echo   [ERROR] Application error (exit code: %EXITCODE%)
)
echo.
echo ============================================================================
echo.

exit /b %EXITCODE%
