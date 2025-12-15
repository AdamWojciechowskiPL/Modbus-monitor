#!/bin/bash
#
# setup.sh - Setup Development Environment
#
# Installs all dependencies and sets up virtual environment
# for development on Linux/macOS
#
# Usage:
#   chmod +x setup.sh
#   ./setup.sh
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "================================================================"
echo " Modbus Monitor - Development Environment Setup"
echo "================================================================"
echo -e "${NC}\n"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}[1/4] Checking Python...${NC}"
python3 --version
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo -e "${GREEN}[2/4] Virtual environment already exists${NC}"
else
    echo -e "${GREEN}[2/4] Creating virtual environment...${NC}"
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo -e "${GREEN}[3/4] Upgrading pip, setuptools, and wheel...${NC}"
pip install --quiet --upgrade pip setuptools wheel
echo -e "${GREEN}Pip upgraded${NC}"
echo ""

# Install dependencies
echo -e "${GREEN}[4/4] Installing all dependencies...${NC}"
pip install --quiet --upgrade -r requirements.txt
pip install --quiet pytest pytest-cov pytest-mock black pylint flake8 mypy pyinstaller
echo -e "${GREEN}All dependencies installed${NC}"

echo ""
echo "================================================================"
echo " Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run development server:"
echo "   python dashboard_app.py"
echo ""
echo "3. Run tests:"
echo "   pytest"
echo ""
echo "4. Build executable:"
echo "   ./build_exe.sh"
echo ""
