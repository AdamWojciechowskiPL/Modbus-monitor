#!/bin/bash

################################################################################
# run.sh - Quick launcher for Modbus Monitor (Linux/macOS with local venv)
################################################################################
#
# This script launches the Modbus Monitor desktop application using the
# local Python installation from the venv directory.
#
# If venv doesn't exist, it will be created and dependencies installed.
#
# Usage:
#   ./run.sh              - Launch normally
#   ./run.sh --help       - Show Python help
#   ./run.sh --version    - Show Python version
#
# Requirements:
#   - Python 3.8+ installed system-wide (for creating venv)
#   - Virtual environment will be auto-created if missing
#
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Paths
VENV_DIR="$SCRIPT_DIR/venv"
PYTHON_EXE="$VENV_DIR/bin/python"
PIP_EXE="$VENV_DIR/bin/pip"

# Print header
echo -e "${BLUE}"
echo ""
echo "============================================================================"
echo ""
echo "  ⚡ Modbus Monitor - Desktop Application Launcher"
echo ""
echo "============================================================================"
echo ""

# Check if venv exists, if not create it
if [ ! -f "$PYTHON_EXE" ]; then
    echo "  [INFO] Virtual environment not found. Creating..."
    echo ""
    
    # Check system Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}"
        echo "  [ERROR] Python 3 not found in PATH!"
        echo ""
        echo "  Please install Python 3.8+:"
        echo "    - Ubuntu/Debian: sudo apt-get install python3 python3-pip"
        echo "    - macOS: brew install python3"
        echo ""
        echo -e "${NC}"
        exit 1
    fi
    
    # Create venv
    echo "  Creating virtual environment in: $VENV_DIR"
    echo ""
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}"
        echo "  [ERROR] Failed to create virtual environment!"
        echo -e "${NC}"
        exit 1
    fi
    echo "  Virtual environment created successfully."
    echo ""
fi

# Get Python version
PYTHON_VERSION=$("$PYTHON_EXE" --version)

echo -e "${GREEN}"
echo "  $PYTHON_VERSION"
echo -e "${BLUE}"
echo "  Using: $PYTHON_EXE"
echo "  Working directory: $SCRIPT_DIR"
echo ""

# Check if modbus_monitor_pyqt.py exists
if [ ! -f "modbus_monitor_pyqt.py" ]; then
    echo -e "${RED}"
    echo "  [ERROR] modbus_monitor_pyqt.py not found in $SCRIPT_DIR"
    echo -e "${NC}"
    exit 1
fi

# Check if PyQt6 is installed
if ! "$PYTHON_EXE" -c "import PyQt6" &> /dev/null; then
    echo -e "${YELLOW}"
    echo "  [INFO] Installing dependencies in venv..."
    echo -e "${NC}"
    echo ""
    "$PIP_EXE" install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}"
        echo "  [ERROR] Failed to install dependencies!"
        echo -e "${NC}"
        exit 1
    fi
    echo ""
fi

echo -e "${BLUE}"
echo "  Starting application..."
echo ""
echo "============================================================================"
echo -e "${NC}"
echo ""

# Launch application with venv Python
echo -e "${GREEN}"
"$PYTHON_EXE" modbus_monitor_pyqt.py "$@"
EXITCODE=$?
echo -e "${BLUE}"

echo ""
if [ $EXITCODE -eq 0 ]; then
    echo -e "${GREEN}  [OK] Application closed successfully.${NC}"
else
    echo -e "${RED}  [ERROR] Application error (exit code: $EXITCODE)${NC}"
fi
echo ""
echo "============================================================================"
echo ""

exit $EXITCODE
