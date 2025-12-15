#!/usr/bin/env python
"""
dashboard_app.py - WebSocket Dashboard Entry Point (Recommended)

This is the recommended Flask application with real-time WebSocket support.
Provides a modern, responsive dashboard with:
- Real-time signal updates
- Interactive charts
- Alert management
- Multi-client support

Usage:
    python dashboard_app.py

Then open http://localhost:5000 in your browser.
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

# Import directly from web module
from modbus_monitor.web.dashboard_app import app, socketio

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    # Ensure exports directory exists
    os.makedirs('exports', exist_ok=True)
    
    print("\n" + "="*70)
    print("🔷 Modbus Monitor - WebSocket Dashboard (Recommended) ⭐")
    print("="*70)
    print(f"🌐 Dashboard: http://localhost:{port}")
    print(f"📊 API: http://localhost:{port}/api/*")
    print(f"🐛 Debug Mode: {debug}")
    print(f"🔌 WebSocket: ws://localhost:{port}/socket.io")
    print("\n💡 Features:")
    print("  ✓ Real-time signal updates (<50ms)")
    print("  ✓ Interactive charts (Chart.js)")
    print("  ✓ Alert management")
    print("  ✓ Multi-client support")
    print("  ✓ Responsive Bootstrap 5 UI")
    print("  ✓ Dark/Light theme")
    print("\n💻 Alternative entry points:")
    print("  - python app.py (Simple Flask, no WebSocket)")
    print("  - python modbus_monitor_pyqt.py (Desktop GUI)")
    print("="*70 + "\n")
    
    # Run Flask app with WebSocket
    try:
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
