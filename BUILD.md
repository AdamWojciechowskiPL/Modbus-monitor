# Modbus Monitor - Build Guide

Complete guide to building and distributing Modbus Monitor for all platforms.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Build Scripts](#build-scripts)
3. [Platform-Specific Instructions](#platform-specific-instructions)
4. [Build Troubleshooting](#build-troubleshooting)
5. [Distribution](#distribution)
6. [Docker](#docker-optional)

---

## Quick Start

### Windows

```bash
# Setup environment
setup.bat

# Build executable
build_exe.bat
```

### Linux / macOS

```bash
# Setup environment
chmod +x setup.sh
./setup.sh

# Build executable
chmod +x build_exe.sh
./build_exe.sh
```

### Universal (All Platforms)

```bash
# Python-based build (works on Windows, Linux, macOS)
python build.py

# Clean and rebuild
python build.py --clean
```

### Using Make (Linux/macOS)

```bash
# Setup
make setup

# Build
make build

# Build with clean
make build-clean

# Run tests
make test
make coverage

# Run application
make web      # WebSocket dashboard (recommended)
make app      # Simple Flask app
make desktop  # Desktop GUI
```

---

## Build Scripts

### 1. `setup.bat` (Windows)

Sets up development environment on Windows.

**Features:**
- Creates virtual environment
- Installs Python dependencies
- Installs development tools
- Guides through next steps

**Usage:**
```bash
setup.bat
```

### 2. `setup.sh` (Linux/macOS)

Sets up development environment on Unix-like systems.

**Features:**
- Creates virtual environment
- Installs Python dependencies
- Installs development tools
- Colored output

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. `build_exe.bat` (Windows)

Builds standalone Windows executable.

**Features:**
- Creates virtual environment if needed
- Installs PyInstaller
- Builds single-file EXE (~150-200 MB)
- Provides distribution instructions

**Usage:**
```bash
build_exe.bat
```

**Output:**
```
dist/modbus_monitor_pyqt.exe
```

### 4. `build_exe.sh` (Linux/macOS)

Builds standalone Linux/macOS executable or app.

**Features:**
- Creates virtual environment if needed
- Detects OS automatically
- For macOS: Creates `.app` bundle
- For Linux: Creates standalone executable
- Optional interactive run after build

**Usage:**
```bash
chmod +x build_exe.sh
./build_exe.sh
```

**Output:**
```
# Linux
dist/modbus_monitor_pyqt

# macOS
dist/modbus_monitor_pyqt.app
```

### 5. `build.py` (Cross-Platform)

Unified Python build script for all platforms.

**Features:**
- Single script for Windows, Linux, macOS
- Automatic platform detection
- Colored output
- Error handling and diagnostics
- Configurable options

**Usage:**
```bash
# Standard build
python build.py

# Clean build (removes old artifacts)
python build.py --clean

# Show help
python build.py --help
```

**Output:**
```
# Windows
dist/modbus_monitor_pyqt.exe

# Linux
dist/modbus_monitor_pyqt

# macOS
dist/modbus_monitor_pyqt.app
```

### 6. `Makefile` (Linux/macOS)

Convenience commands for development.

**Common Targets:**
```bash
make help             # Show all targets
make setup            # Setup environment
make install          # Install dependencies
make install-dev      # Install with dev tools
make test             # Run tests
make coverage         # Run tests with coverage
make build            # Build executable
make build-clean      # Clean and rebuild
make web              # Run WebSocket dashboard
make app              # Run Flask app
make desktop          # Run desktop GUI
make format           # Format code with black
make lint             # Run code quality checks
make clean            # Clean build artifacts
```

---

## Platform-Specific Instructions

### Windows

#### Prerequisites
- Python 3.8+ (with "Add Python to PATH" checked)
- Git (optional)
- 1 GB free disk space

#### Build Steps

```bash
# 1. Clone repository or extract ZIP
cd modbus-monitor

# 2. Run setup
setup.bat

# 3. Verify setup
venv\Scripts\python --version

# 4. Build executable
build_exe.bat

# 5. Test the build
dist\modbus_monitor_pyqt.exe

# 6. Create installer (optional)
# You can use NSIS, Inno Setup, or similar to create an installer
```

#### System Requirements (End User)
- Windows 7+
- 512 MB RAM
- 200 MB free disk space
- No Python installation required

### Linux

#### Prerequisites
- Python 3.8+
- pip / venv
- libGL, libxkbcommon, libdbus-1 (for PyQt6)
- 1 GB free disk space

#### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv

# For PyQt6 GUI
sudo apt-get install libgl1-mesa-glx libxkbcommon-x11-0 libdbus-1-3

# Clone and build
cd modbus-monitor
chmod +x setup.sh build_exe.sh
./setup.sh
./build_exe.sh

# Test
./dist/modbus_monitor_pyqt
```

#### Fedora/RHEL

```bash
# Install system dependencies
sudo dnf install python3-devel python3-pip
sudo dnf install mesa-libGL libxkbcommon libdbus-1

# Build
chmod +x setup.sh build_exe.sh
./setup.sh
./build_exe.sh
```

#### Arch

```bash
# Install system dependencies
sudo pacman -S python pip

# Build
chmod +x setup.sh build_exe.sh
./setup.sh
./build_exe.sh
```

#### System Requirements (End User)
- Python 3.8+
- LibGL and related packages
- 512 MB RAM
- 200 MB free disk space

### macOS

#### Prerequisites
- Python 3.8+ (via Homebrew or python.org)
- Xcode Command Line Tools
- 1 GB free disk space

#### Installation

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Install Xcode Command Line Tools
xcode-select --install

# Clone and build
cd modbus-monitor
chmod +x setup.sh build_exe.sh
./setup.sh
./build_exe.sh

# Test
open dist/modbus_monitor_pyqt.app
```

#### Create DMG (Distribution)

```bash
# Create DMG for distribution
hdiutil create -volname "Modbus Monitor" -srcfolder dist -ov modbus_monitor.dmg
```

#### System Requirements (End User)
- macOS 10.13+
- 512 MB RAM
- 200 MB free disk space

---

## Build Troubleshooting

### Issue: "Python not found"

**Windows:**
```bash
# Make sure Python is in PATH
python --version

# If not, add to PATH or use full path
C:\Python310\python.exe build.py
```

**Linux/macOS:**
```bash
python3 --version

# Use python3 explicitly
python3 build.py
```

### Issue: "PyInstaller failed"

```bash
# Update PyInstaller
pip install --upgrade pyinstaller

# Rebuild with verbose output
pyinstaller --debug modbus_monitor_pyqt.py
```

### Issue: "Permission denied" on Linux/macOS

```bash
# Make scripts executable
chmod +x build_exe.sh setup.sh

# Run again
./build_exe.sh
```

### Issue: "No module named PyQt6"

```bash
# Ensure PyQt6 is installed
pip install PyQt6 PyQt6-Charts

# Try building again
python build.py
```

### Issue: Build size too large

**Typical sizes:**
- Windows: 150-200 MB
- Linux: 150-200 MB
- macOS: 300-400 MB (includes macOS runtime)

This is normal. PyInstaller bundles Python runtime and all dependencies.

### Issue: "Icon not found"

```bash
# Icons are optional, build will work without them
# To use icons:
# Windows: Place modbus_icon.ico in project root
# macOS: Place modbus_icon.icns in project root
```

---

## Distribution

### Windows Distribution

**As EXE:**
1. Locate `dist/modbus_monitor_pyqt.exe`
2. Copy to target machine
3. Run directly (no installation needed)

**With Installer:**
```bash
# Using Inno Setup
# Create modbus_monitor.iss and build installer
```

### Linux Distribution

**As AppImage:**
```bash
# Install appimagetool
sudo apt-get install appimagetool

# Create AppImage
appimagetool dist/modbus_monitor_pyqt modbus_monitor_pyqt.AppImage

# Users can run directly or install to ~/.local/bin
```

**As DEB/RPM:**
```bash
# Create DEB package
fpm -s dir -t deb -n modbus-monitor -v 1.0 -C dist modbus_monitor_pyqt=/usr/bin/
```

### macOS Distribution

**As DMG:**
```bash
hdiutil create -volname "Modbus Monitor" -srcfolder dist -ov modbus_monitor.dmg
```

**As ZIP:**
```bash
zip -r modbus_monitor.zip dist/modbus_monitor_pyqt.app
```

---

## Docker (Optional)

Create containerized version for deployment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "dashboard_app.py"]
```

**Build and run:**
```bash
docker build -t modbus-monitor .
docker run -p 5000:5000 modbus-monitor
```

---

## Build Performance

**Typical build times:**
- Setup: 2-5 minutes (first run)
- Build: 2-5 minutes
- Total: 4-10 minutes

**To speed up builds:**
```bash
# Skip virtual environment creation
python build.py --no-venv

# Use cached build
make build  # Uses existing setup
```

---

## Verification

After building, verify the executable works:

```bash
# Windows
dist\modbus_monitor_pyqt.exe --help

# Linux
./dist/modbus_monitor_pyqt --help

# macOS
open dist/modbus_monitor_pyqt.app
```

---

## Support

For build issues:

1. Check BUILD.md (this file)
2. Check README.md for requirements
3. Check test results: `pytest`
4. Open GitHub issue with:
   - OS and Python version
   - Error message and logs
   - Build script used

---

**Happy building!** 🚀
