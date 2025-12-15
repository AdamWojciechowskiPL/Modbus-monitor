#!/bin/bash
#
# build_exe.sh - Build standalone executable for Linux/macOS with PyInstaller
#
# Usage:
#   chmod +x build_exe.sh
#   ./build_exe.sh
#
# Output: dist/modbus_monitor_pyqt (Linux) or dist/modbus_monitor_pyqt.app (macOS)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "================================================================"
echo " Modbus Monitor - PyInstaller Build Script (Linux/macOS)"
echo "================================================================"
echo -e "${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed or not in PATH${NC}"
    echo ""
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}[1/6] Checking Python version...${NC}"
python3 --version
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${GREEN}[2/6] Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${GREEN}[2/6] Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi
echo ""

# Upgrade pip
echo -e "${GREEN}[3/6] Upgrading pip and installing dependencies...${NC}"
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet -r requirements.txt
pip install --quiet pyinstaller
echo ""

# Check PyInstaller
echo -e "${GREEN}[4/6] Checking PyInstaller installation...${NC}"
pyinstaller --version
echo ""

# Detect OS
OS="$(uname -s)"
echo -e "${BLUE}Detected OS: ${OS}${NC}"
echo ""

# Remove old build/dist
echo -e "${YELLOW}[5/6] Cleaning previous builds...${NC}"
rm -rf build dist *.spec
echo ""

# Build with PyInstaller
echo -e "${GREEN}[5/6] Building executable with PyInstaller...${NC}"
echo "This may take 2-5 minutes..."
echo ""

if [ "$OS" = "Darwin" ]; then
    # macOS specific build
    pyinstaller --name="modbus_monitor_pyqt" \
        --onefile \
        --windowed \
        --icon=modbus_icon.icns \
        --add-data="modbus_monitor/gui:modbus_monitor/gui" \
        --add-data="modbus_monitor/web:modbus_monitor/web" \
        --add-data=".env.example:." \
        --hidden-import=PyQt6.QtCore \
        --hidden-import=PyQt6.QtGui \
        --hidden-import=PyQt6.QtWidgets \
        --hidden-import=PyQt6.QtCharts \
        --hidden-import=pymodbus \
        --hidden-import=sqlalchemy \
        --hidden-import=pandas \
        --hidden-import=openpyxl \
        --osx-bundle-identifier=com.modbusmonitor.app \
        --noconfirm \
        modbus_monitor_pyqt.py
else
    # Linux specific build
    pyinstaller --name="modbus_monitor_pyqt" \
        --onefile \
        --windowed \
        --add-data="modbus_monitor/gui:modbus_monitor/gui" \
        --add-data="modbus_monitor/web:modbus_monitor/web" \
        --add-data=".env.example:." \
        --hidden-import=PyQt6.QtCore \
        --hidden-import=PyQt6.QtGui \
        --hidden-import=PyQt6.QtWidgets \
        --hidden-import=PyQt6.QtCharts \
        --hidden-import=pymodbus \
        --hidden-import=sqlalchemy \
        --hidden-import=pandas \
        --hidden-import=openpyxl \
        --noconfirm \
        modbus_monitor_pyqt.py
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}\n[ERROR] PyInstaller build failed!${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "- Check that all dependencies are installed"
    echo "- Verify modbus_icon.icns/.ico exists (optional)"
    echo "- Try: pip install --upgrade pyinstaller"
    exit 1
fi

echo ""
echo -e "${GREEN}[6/6] Build complete!${NC}"
echo ""
echo "================================================================"
echo " Build Summary"
echo "================================================================"
echo ""

if [ "$OS" = "Darwin" ]; then
    OUTPUT="dist/modbus_monitor_pyqt.app"
    echo -e "${GREEN}Output: ${OUTPUT}${NC}"
    echo ""
    echo "To run the application:"
    echo "  open dist/modbus_monitor_pyqt.app"
    echo ""
    echo "To distribute:"
    echo "  - Copy dist/modbus_monitor_pyqt.app to target machine"
    echo "  - Or create DMG: hdiutil create -volname \"Modbus Monitor\" -srcfolder dist -ov modbus_monitor.dmg"
else
    OUTPUT="dist/modbus_monitor_pyqt"
    echo -e "${GREEN}Output: ${OUTPUT}${NC}"
    SIZE=$(ls -lh "$OUTPUT" 2>/dev/null | awk '{print $5}')
    echo "Size: $SIZE"
    echo ""
    echo "To run the application:"
    echo "  ./dist/modbus_monitor_pyqt"
    echo ""
    echo "To distribute:"
    echo "  - Copy dist/modbus_monitor_pyqt to target machine"
    echo "  - No Python installation required!"
fi

echo ""
echo "================================================================"
echo ""

# Ask if user wants to run the app
read -p "Would you like to run the application now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$OS" = "Darwin" ]; then
        open dist/modbus_monitor_pyqt.app
    else
        ./dist/modbus_monitor_pyqt
    fi
fi
