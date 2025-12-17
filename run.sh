#!/bin/bash

################################################################################
# run.sh - Quick launcher for Modbus Monitor (Linux/macOS)
################################################################################
#
# This script launches the Modbus Monitor desktop application using the
# system Python installation.
#
# Usage:
#   ./run.sh              - Launch normally
#   ./run.sh --help       - Show Python help
#   ./run.sh --version    - Show Python version
#
# Requirements:
#   - Python 3.8+ in PATH
#   - Dependencies installed: pip install -r requirements.txt
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

# Print header
echo -e "${BLUE}"
echo ""
echo "============================================================================"
echo ""
echo "  ⚡ Modbus Monitor - Desktop Application Launcher"
echo ""
echo "============================================================================"
echo ""

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}"
    echo "[ERROR] Python 3 not found in PATH!"
    echo ""
    echo "Please install Python 3.8+:"
    echo "  - Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  - macOS: brew install python3"
    echo ""
    echo "After installation, run: pip3 install -r requirements.txt"
    echo ""
    echo -e "${NC}"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version)
echo "  $PYTHON_VERSION"
echo "  Working directory: $(pwd)"
echo ""
echo "  Starting application..."
echo ""
echo "============================================================================"
echo -e "${NC}"
echo ""

# Check if modbus_monitor_pyqt.py exists
if [ ! -f "modbus_monitor_pyqt.py" ]; then
    echo -e "${RED}"
    echo "[ERROR] modbus_monitor_pyqt.py not found in $(pwd)"
    echo -e "${NC}"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import PyQt6" &> /dev/null; then
    echo -e "${YELLOW}"
    echo "[WARNING] Dependencies not found!"
    echo ""
    echo "Installing dependencies... This may take a few minutes."
    echo ""
    echo -e "${NC}"
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}"
        echo "[ERROR] Failed to install dependencies!"
        echo -e "${NC}"
        exit 1
    fi
fi

# Launch application
echo -e "${GREEN}"
python3 modbus_monitor_pyqt.py "$@"
EXITCODE=$?

echo -e "${NC}"

if [ $EXITCODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Application closed successfully.${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}Application error (exit code: $EXITCODE)${NC}"
    echo ""
fi

exit $EXITCODE
