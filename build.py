#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build.py - Unified Cross-Platform Build Script

Supports building for Windows, Linux, and macOS
Creates standalone executables with PyInstaller

Usage:
    python build.py                    # Interactive mode
    python build.py --clean            # Clean build artifacts
    python build.py --help             # Show help
"""

import os
import sys
import subprocess
import shutil
import platform
import argparse
from pathlib import Path
import io

# Fix Unicode output on Windows
if sys.platform == 'win32':
    # Reconfigure stdout to use UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")


class ModbusMonitorBuilder:
    """Builder for Modbus Monitor project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform = platform.system()
        self.venv_path = self.project_root / "venv"
        self.dist_path = self.project_root / "dist"
        self.build_path = self.project_root / "build"
    
    def check_python(self):
        """Check Python version"""
        print_info(f"Checking Python version...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_error(f"Python 3.8+ required. Found: {version.major}.{version.minor}")
            return False
        print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
        return True
    
    def create_venv(self):
        """Create virtual environment"""
        if self.venv_path.exists():
            print_info("Virtual environment already exists")
        else:
            print_info("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)
            print_success("Virtual environment created")
    
    def get_venv_python(self):
        """Get Python executable path in venv"""
        if self.platform == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def install_dependencies(self):
        """Install project dependencies"""
        print_info("Installing dependencies...")
        venv_python = self.get_venv_python()
        
        # Upgrade pip
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
            check=True
        )
        
        # Install requirements
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--quiet", "-r", "requirements.txt"],
            check=True,
            cwd=self.project_root
        )
        
        # Install PyInstaller
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--quiet", "pyinstaller"],
            check=True
        )
        
        print_success("Dependencies installed")
    
    def clean_build(self):
        """Clean build artifacts"""
        print_info("Cleaning build artifacts...")
        
        if self.build_path.exists():
            shutil.rmtree(self.build_path)
            print_success(f"Removed {self.build_path}")
        
        if self.dist_path.exists():
            shutil.rmtree(self.dist_path)
            print_success(f"Removed {self.dist_path}")
        
        # Remove .spec files
        for spec_file in self.project_root.glob("*.spec"):
            spec_file.unlink()
            print_success(f"Removed {spec_file}")
    
    def check_icon(self):
        """Check if icon file exists for current platform"""
        if self.platform == "Windows":
            icon_file = self.project_root / "modbus_icon.ico"
        elif self.platform == "Darwin":
            icon_file = self.project_root / "modbus_icon.icns"
        else:  # Linux
            icon_file = None
        
        if icon_file is None:
            print_info("Icon not required for Linux")
            return None
        
        if icon_file.exists():
            print_success(f"Icon found: {icon_file}")
            return icon_file
        else:
            print_warning(f"Icon not found: {icon_file}")
            print_info("Build will continue without icon")
            return None
    
    def build_exe(self):
        """Build standalone executable with PyInstaller"""
        print_info("Building executable...")
        
        venv_python = self.get_venv_python()
        
        # Get PyInstaller path
        if self.platform == "Windows":
            pyinstaller = self.venv_path / "Scripts" / "pyinstaller"
        else:
            pyinstaller = self.venv_path / "bin" / "pyinstaller"
        
        # Common PyInstaller arguments
        args = [
            str(pyinstaller),
            "--name=modbus_monitor_pyqt",
            "--onefile",
            "--windowed",
            "--add-data=modbus_monitor/gui:modbus_monitor/gui",
            "--add-data=.env.example:.",
            "--hidden-import=PyQt6.QtCore",
            "--hidden-import=PyQt6.QtGui",
            "--hidden-import=PyQt6.QtWidgets",
            "--hidden-import=PyQt6.QtCharts",
            "--hidden-import=pymodbus",
            "--hidden-import=sqlalchemy",
            "--hidden-import=pandas",
            "--hidden-import=openpyxl",
            "--noconfirm",
            "modbus_monitor_pyqt.py"
        ]
        
        # Check for icon and add if exists
        icon_file = self.check_icon()
        if icon_file:
            if self.platform == "Windows":
                args.insert(3, f"--icon={icon_file}")
            elif self.platform == "Darwin":
                args.insert(3, f"--icon={icon_file}")
        
        # Platform-specific arguments
        if self.platform == "Darwin":  # macOS
            args.extend(["--osx-bundle-identifier=com.modbusmonitor.app"])
        
        # Run PyInstaller
        print_info(f"Building for {self.platform}...")
        print_info("This may take 2-5 minutes...")
        
        try:
            # Capture output for better error reporting
            result = subprocess.run(
                args,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode != 0:
                print_error(f"Build failed with exit code {result.returncode}")
                print_info("Troubleshooting tips:")
                print_info("  1. Check that .env.example exists in project root")
                print_info("  2. Check that modbus_monitor/gui directory exists")
                print_info("  3. Try: python build.py --clean")
                print_info("  4. Check PyInstaller version: pyinstaller --version")
                return False
            
            print_success("Build completed successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            print_error(f"Build failed: {e}")
            return False
        except Exception as e:
            print_error(f"Unexpected error during build: {e}")
            return False
    
    def show_build_info(self):
        """Show build information"""
        print_header("Build Summary")
        
        if self.platform == "Windows":
            exe_path = self.dist_path / "modbus_monitor_pyqt.exe"
            label = "Output"
        elif self.platform == "Darwin":
            exe_path = self.dist_path / "modbus_monitor_pyqt.app"
            label = "Output (macOS app)"
        else:
            exe_path = self.dist_path / "modbus_monitor_pyqt"
            label = "Output (Linux executable)"
        
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)
            print_success(f"{label}: {exe_path}")
            print_info(f"Size: {size:.1f} MB")
            
            print_info("\nHow to run:")
            if self.platform == "Windows":
                print(f"  {exe_path}")
            elif self.platform == "Darwin":
                print(f"  open {exe_path}")
            else:
                print(f"  ./{exe_path}")
            
            print_info("\nDistribution:")
            if self.platform == "Windows":
                print("  - Copy modbus_monitor_pyqt.exe to target machine")
                print("  - No Python installation required!")
            elif self.platform == "Darwin":
                print("  - Copy modbus_monitor_pyqt.app to /Applications")
                print("  - Or create DMG for distribution")
            else:
                print("  - Copy modbus_monitor_pyqt to target machine")
                print("  - May require system libraries (libGL, etc)")
        else:
            # Try to find output anyway
            if self.dist_path.exists():
                files = list(self.dist_path.glob("*"))
                if files:
                    print_warning(f"Build output location may differ:")
                    for f in files[:5]:
                        print(f"  - {f}")
            else:
                print_error(f"Build output not found: {exe_path}")
                print_warning("Check dist/ directory")
    
    def build(self, clean=False):
        """Execute full build process"""
        print_header("Modbus Monitor - Build Script")
        print_info(f"Platform: {self.platform}")
        print_info(f"Python: {sys.version.split()[0]}")
        
        # Check Python
        if not self.check_python():
            print_error("Build failed")
            return False
        
        # Clean if requested
        if clean:
            self.clean_build()
        
        # Create virtual environment
        self.create_venv()
        
        # Install dependencies
        self.install_dependencies()
        
        # Clean old builds
        self.clean_build()
        
        # Build executable
        if self.build_exe():
            self.show_build_info()
            print_success("\nBuild process completed successfully!")
            return True
        else:
            print_error("Build process failed")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Build Modbus Monitor standalone executable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Interactive build
  python build.py --clean            # Clean and rebuild
  python build.py --help             # Show this help
        """
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    parser.add_argument(
        "--no-venv",
        action="store_true",
        help="Skip virtual environment creation (use system Python)"
    )
    
    args = parser.parse_args()
    
    builder = ModbusMonitorBuilder()
    
    try:
        success = builder.build(clean=args.clean)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nBuild interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
