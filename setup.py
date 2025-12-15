# setup.py - Setuptools Configuration

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    # Basic Information
    name="modbus-monitor",
    version="1.0.0",
    description="Professional Modbus TCP/RTU monitoring application with real-time dashboard, alerts, and data export",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/modbus-monitor",
    project_urls={
        "Documentation": "https://github.com/yourusername/modbus-monitor/wiki",
        "Source Code": "https://github.com/yourusername/modbus-monitor",
        "Bug Tracker": "https://github.com/yourusername/modbus-monitor/issues",
    },
    
    # License
    license="MIT",
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Web Environment :: Browsers",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Polish",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking",
    ],
    
    # Python Version
    python_requires=">=3.8",
    
    # Packages
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    
    # Core Dependencies (minimal)
    install_requires=[
        "Flask>=2.3.0",
        "pymodbus>=3.1.0",
        "python-dotenv>=1.0.0",
        "SQLAlchemy>=2.0.0",
        "openpyxl>=3.1.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
    ],
    
    # Optional Dependencies (extras)
    extras_require={
        # Web Dashboard with WebSocket
        "web": [
            "Flask-SocketIO>=5.3.0",
            "python-socketio>=5.9.0",
            "python-engineio>=4.7.0",
        ],
        
        # Desktop PyQt6 Application
        "desktop": [
            "PyQt6>=6.5.0",
            "PyQt6-Charts>=6.5.0",
        ],
        
        # Alerts & Notifications
        "alerts": [
            "plyer>=2.1.0",
            "email-validator>=2.0.0",
        ],
        
        # Database - PostgreSQL
        "postgres": [
            "psycopg2-binary>=2.9.0",
        ],
        
        # Build - Create EXE
        "build": [
            "pyinstaller>=6.1.0",
            "wheel>=0.41.0",
        ],
        
        # Development Tools
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "pylint>=2.17.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        
        # All extras
        "all": [
            "Flask-SocketIO>=5.3.0",
            "python-socketio>=5.9.0",
            "python-engineio>=4.7.0",
            "PyQt6>=6.5.0",
            "PyQt6-Charts>=6.5.0",
            "plyer>=2.1.0",
            "email-validator>=2.0.0",
            "psycopg2-binary>=2.9.0",
            "pyinstaller>=6.1.0",
            "pytest>=7.4.0",
            "black>=23.7.0",
            "pylint>=2.17.0",
        ],
    },
    
    # Entry Points (optional - dla setuptools console scripts)
    entry_points={
        "console_scripts": [
            "modbus-monitor=modbus_monitor_pyqt:main",
        ],
    },
    
    # Package Data
    package_data={
        "": [
            "*.html",
            "*.js",
            "*.css",
            "*.json",
            "*.md",
        ],
    },
    
    # Include Data Files
    include_package_data=True,
    
    # Zip Safe
    zip_safe=False,
    
    # Keywords
    keywords=[
        "modbus",
        "monitoring",
        "industrial",
        "IoT",
        "dashboard",
        "real-time",
        "TCP",
        "RTU",
        "serial",
        "alerts",
    ],
    
    # Documentation
    documentation_url="https://github.com/yourusername/modbus-monitor/wiki",
    
    # Python Implementation
    python_requires=">=3.8",
)
