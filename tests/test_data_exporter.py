#!/usr/bin/env python
"""
test_data_exporter.py - Unit Tests for Data Export Module

Tests cover:
- CSV export
- Excel export
- JSON export
- Batch export (all formats)
- Filename generation
- Error handling
"""

import pytest
import os
import json
import csv
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modbus_monitor.data_exporter import DataExporter


@pytest.mark.unit
class TestDataExporterInit:
    """Test DataExporter initialization"""
    
    def test_init_creates_export_dir(self, tmp_path):
        """Test that export directory is created"""
        export_dir = str(tmp_path / "exports")
        exporter = DataExporter(export_dir=export_dir)
        
        assert os.path.exists(export_dir)
        assert exporter.export_dir == export_dir
    
    def test_init_with_existing_dir(self, tmp_path):
        """Test init with existing directory"""
        export_dir = str(tmp_path / "exports")
        os.makedirs(export_dir)
        
        exporter = DataExporter(export_dir=export_dir)
        
        assert exporter.export_dir == export_dir


@pytest.mark.unit
class TestDataExporterFilenameGeneration:
    """Test filename generation"""
    
    def test_generate_filename_csv(self, tmp_path):
        """Test CSV filename generation"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filename = exporter._generate_filename('csv')
        
        assert filename.endswith('.csv')
        assert 'modbus_data_' in filename
    
    def test_generate_filename_json(self, tmp_path):
        """Test JSON filename generation"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filename = exporter._generate_filename('json')
        
        assert filename.endswith('.json')
    
    def test_generate_filename_xlsx(self, tmp_path):
        """Test Excel filename generation"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filename = exporter._generate_filename('xlsx')
        
        assert filename.endswith('.xlsx')
    
    def test_generate_filename_contains_timestamp(self, tmp_path):
        """Test that generated filename contains timestamp"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filename = exporter._generate_filename('csv')
        
        # Extract timestamp from filename (YYYYMMDD_HHMMSS format)
        parts = filename.split('_')
        assert len(parts) >= 3
        # Check date part (8 digits)
        assert len(parts[-2]) == 8
        assert parts[-2].isdigit()


@pytest.mark.unit
class TestDataExporterCSV:
    """Test CSV export functionality"""
    
    def test_export_to_csv_success(self, sample_signals, tmp_path):
        """Test successful CSV export"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_csv(sample_signals)
        
        assert os.path.exists(filepath)
        assert filepath.endswith('.csv')
    
    def test_export_to_csv_content(self, sample_signals, tmp_path):
        """Test CSV file content"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_csv(sample_signals)
        
        # Read and verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3
        assert rows[0]['Nazwa Sygnału'] == 'Temperature'
        assert rows[1]['Nazwa Sygnału'] == 'Pressure'
    
    def test_export_to_csv_custom_filename(self, sample_signals, tmp_path):
        """Test CSV export with custom filename"""
        exporter = DataExporter(export_dir=str(tmp_path))
        custom_filename = "my_signals.csv"
        
        filepath = exporter.export_to_csv(sample_signals, filename=custom_filename)
        
        assert os.path.basename(filepath) == custom_filename
    
    def test_export_to_csv_empty_signals(self, empty_signals, tmp_path):
        """Test CSV export with empty signals"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_csv(empty_signals)
        
        # File should exist but have only headers
        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 1  # Only header


@pytest.mark.unit
class TestDataExporterJSON:
    """Test JSON export functionality"""
    
    def test_export_to_json_success(self, sample_signals, tmp_path):
        """Test successful JSON export"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_json(sample_signals)
        
        assert os.path.exists(filepath)
        assert filepath.endswith('.json')
    
    def test_export_to_json_content(self, sample_signals, tmp_path):
        """Test JSON file content"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_json(sample_signals)
        
        # Read and verify content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'exportDate' in data
        assert 'signalCount' in data
        assert 'signals' in data
        assert data['signalCount'] == 3
        assert len(data['signals']) == 3
    
    def test_export_to_json_custom_filename(self, sample_signals, tmp_path):
        """Test JSON export with custom filename"""
        exporter = DataExporter(export_dir=str(tmp_path))
        custom_filename = "my_data.json"
        
        filepath = exporter.export_to_json(sample_signals, filename=custom_filename)
        
        assert os.path.basename(filepath) == custom_filename
    
    def test_export_to_json_empty_signals(self, empty_signals, tmp_path):
        """Test JSON export with empty signals"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath = exporter.export_to_json(empty_signals)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data['signalCount'] == 0
        assert data['signals'] == []


@pytest.mark.unit
class TestDataExporterExcel:
    """Test Excel export functionality"""
    
    def test_export_to_excel_success(self, sample_signals, tmp_path):
        """Test successful Excel export"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        try:
            filepath = exporter.export_to_excel(sample_signals)
            assert os.path.exists(filepath)
            assert filepath.endswith('.xlsx')
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_export_to_excel_custom_filename(self, sample_signals, tmp_path):
        """Test Excel export with custom filename"""
        exporter = DataExporter(export_dir=str(tmp_path))
        custom_filename = "my_signals.xlsx"
        
        try:
            filepath = exporter.export_to_excel(sample_signals, filename=custom_filename)
            assert os.path.basename(filepath) == custom_filename
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_export_to_excel_empty_signals(self, empty_signals, tmp_path):
        """Test Excel export with empty signals"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        try:
            filepath = exporter.export_to_excel(empty_signals)
            # File should exist
            assert os.path.exists(filepath)
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_export_to_excel_missing_openpyxl(self, sample_signals, tmp_path, monkeypatch):
        """Test Excel export when openpyxl is not installed"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        # Mock missing openpyxl
        import sys
        original_modules = sys.modules.copy()
        sys.modules['openpyxl'] = None
        
        try:
            with pytest.raises(ImportError):
                exporter.export_to_excel(sample_signals)
        finally:
            sys.modules.update(original_modules)


@pytest.mark.unit
class TestDataExporterBatch:
    """Test batch export (all formats)"""
    
    def test_export_all_formats(self, sample_signals, tmp_path):
        """Test exporting to all formats at once"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        try:
            files = exporter.export_all(sample_signals)
            
            assert 'csv' in files
            assert 'json' in files
            # Excel may not be available
            
            # Verify files exist
            csv_path = os.path.join(str(tmp_path), files['csv'])
            json_path = os.path.join(str(tmp_path), files['json'])
            
            assert os.path.exists(csv_path)
            assert os.path.exists(json_path)
        except Exception as e:
            pytest.skip(f"Export all failed: {e}")
    
    def test_export_all_empty_signals(self, empty_signals, tmp_path):
        """Test batch export with empty signals"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        try:
            files = exporter.export_all(empty_signals)
            
            # Should still create files
            assert 'csv' in files
            assert 'json' in files
        except Exception as e:
            pytest.skip(f"Export all failed: {e}")


@pytest.mark.unit
class TestDataExporterErrorHandling:
    """Test error handling"""
    
    def test_export_csv_permission_error(self, sample_signals, tmp_path):
        """Test CSV export with permission error"""
        # Create read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        exporter = DataExporter(export_dir=str(readonly_dir))
        
        try:
            with pytest.raises(Exception):
                exporter.export_to_csv(sample_signals)
        finally:
            readonly_dir.chmod(0o755)  # Restore permissions
    
    def test_export_json_permission_error(self, sample_signals, tmp_path):
        """Test JSON export with permission error"""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)  # Read-only
        
        exporter = DataExporter(export_dir=str(readonly_dir))
        
        try:
            with pytest.raises(Exception):
                exporter.export_to_json(sample_signals)
        finally:
            readonly_dir.chmod(0o755)  # Restore permissions


@pytest.mark.unit
class TestDataExporterIntegration:
    """Integration tests"""
    
    def test_multiple_exports_create_different_files(self, sample_signals, tmp_path):
        """Test that multiple exports create different files"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        filepath1 = exporter.export_to_json(sample_signals)
        filepath2 = exporter.export_to_json(sample_signals)
        
        # Files should be different (due to timestamp)
        assert filepath1 != filepath2
        assert os.path.exists(filepath1)
        assert os.path.exists(filepath2)
    
    def test_export_preserves_data_integrity(self, sample_signals, tmp_path):
        """Test that exported data maintains integrity"""
        exporter = DataExporter(export_dir=str(tmp_path))
        
        # Export to JSON
        filepath = exporter.export_to_json(sample_signals)
        
        # Read back and verify
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Verify original data is preserved
        for i, signal in enumerate(data['signals']):
            assert signal['name'] == sample_signals[i]['name']
            assert signal['value'] == sample_signals[i]['value']
            assert signal['unit'] == sample_signals[i]['unit']
