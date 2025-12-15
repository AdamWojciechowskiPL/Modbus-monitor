# tests/conftest.py
import pytest
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

# Pytest configuration
@pytest.fixture
def sample_signals():
    """Sample signals for testing"""
    return [
        {'name': 'Signal1', 'value': 42.5, 'unit': '°C'},
        {'name': 'Signal2', 'value': 100.0, 'unit': '%'},
    ]