#!/usr/bin/env python
"""
app.py - Flask Web Application Entry Point (Simple)

This is a simple Flask application for Modbus monitoring.
For WebSocket support and real-time dashboard, use dashboard_app.py instead.

Usage:
    python app.py

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

# Import Flask app directly from web module
from modbus_monitor.web.app import app

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    
    # Ensure exports directory exists
    os.makedirs('exports', exist_ok=True)
    
    print("\n" + "="*70)
    print("🔷 Modbus Monitor - Flask Web Application")
    print("="*70)
    print(f"🌐 Server: http://localhost:{port}")
    print(f"📊 Dashboard: http://localhost:{port}/")
    print(f"🔌 API: http://localhost:{port}/api/*")
    print(f"🐛 Debug Mode: {debug}")
    print("\n💡 For real-time WebSocket dashboard, use: python dashboard_app.py")
    print("💻 For desktop GUI, use: python modbus_monitor_pyqt.py")
    print("="*70 + "\n")
    
    # Run Flask app
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
