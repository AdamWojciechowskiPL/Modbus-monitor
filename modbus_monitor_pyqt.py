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

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔷 Modbus Monitor - PyQt6 Desktop Application")
    print("="*70)
    print("📄 Starting PyQt6 desktop interface...\n")
    
    try:
        # Import PyQt6 application
        from modbus_monitor.gui.modbus_monitor_pyqt import main
        
        print("💡 Features:")
        print("  ✓ Native Qt interface")
        print("  ✓ Real-time signals table")
        print("  ✓ Alert management")
        print("  ✓ Data export (CSV, Excel, JSON)")
        print("  ✓ Dark theme support")
        print("\n💻 Alternative entry points:")
        print("  - python app.py (Simple Flask web)")
        print("  - python dashboard_app.py (WebSocket dashboard)")
        print("\n" + "="*70 + "\n")
        
        # Run PyQt6 application
        main()
        
    except ImportError as e:
        print(f"\n❌ PyQt6 Error: {e}")
        print("\n📄 Installation instructions:")
        print("\nOption 1 - Install desktop dependencies:")
        print("  pip install -e \".[desktop]\"")
        print("\nOption 2 - Install PyQt6 packages manually:")
        print("  pip install PyQt6 PyQt6-Charts")
        print("\nOption 3 - Use web interface instead:")
        print("  python dashboard_app.py")
        print()
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Application stopped by user.")
    
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
