#!/usr/bin/env python
"""
modbus_monitor_pyqt.py - PyQt6 Desktop Application Entry Point

This is a native PyQt6 desktop application for Modbus monitoring.
Provides a rich desktop experience with:
- Native Qt interface
- Dark theme support
- Real-time signals table
- QChart visualizations
- Alert management
- Data export (CSV, Excel, JSON)
- Connection management

Usage:
    python modbus_monitor_pyqt.py

Or build standalone EXE:
    build_exe.bat  (Windows)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import PyQt6 application
from modbus_monitor.gui.modbus_monitor_pyqt import main

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔷 Modbus Monitor - PyQt6 Desktop Application")
    print("="*60)
    print("📄 Starting PyQt6 desktop interface...")
    print("\n💡 Features:")
    print("  ✓ Native Qt interface")
    print("  ✓ Real-time signals table")
    print("  ✓ QChart visualizations")
    print("  ✓ Alert management")
    print("  ✓ Data export (CSV, Excel, JSON)")
    print("  ✓ Dark theme support")
    print("\n💻 Alternative entry points:")
    print("  - app.py (Simple Flask web)")
    print("  - dashboard_app.py (WebSocket dashboard)")
    print("="*60 + "\n")
    
    try:
        # Run PyQt6 application
        main()
    except ImportError as e:
        print(f"\n❌ PyQt6 not installed: {e}")
        print("\nInstall with: pip install PyQt6 PyQt6-Charts")
        print("Or: pip install -e \".[desktop]\"")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Application stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
