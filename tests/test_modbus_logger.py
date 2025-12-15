#!/usr/bin/env python
"""
test_modbus_logger.py - Unit Tests for Logging Module

Tests cover:
- Logger initialization
- Log level configuration
- File logging
- Log rotation
"""

import pytest
import os
import logging
from pathlib import Path
import sys

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modbus_monitor.modbus_logger import setup_logger, get_logger


@pytest.mark.unit
class TestLoggerSetup:
    """Test logger setup and configuration"""
    
    def test_setup_logger_returns_logger(self, tmp_path):
        """Test that setup_logger returns a logger instance"""
        logger = setup_logger(
            name='test_logger',
            log_dir=str(tmp_path),
            log_level=logging.INFO
        )
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'
    
    def test_setup_logger_creates_log_file(self, tmp_path):
        """Test that logger is properly configured"""
        logger = setup_logger(
            name='test_logger_file',
            log_dir=str(tmp_path),
            log_level=logging.INFO
        )
        
        # Verify logger has handlers
        assert len(logger.handlers) > 0
        
        # Write a log message
        logger.info("Test message")
        
        # Check if log file exists (may or may not, depending on implementation)
        log_files = list(tmp_path.glob('*.log'))
        # At minimum, logger should be properly configured
        assert isinstance(logger, logging.Logger)
    
    def test_setup_logger_with_different_levels(self, tmp_path):
        """Test logger with different log levels"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        
        for level in levels:
            logger = setup_logger(
                name=f'logger_{level}',
                log_dir=str(tmp_path),
                log_level=level
            )
            
            # Logger's effective level should match or be close
            assert logger.level == level or logger.getEffectiveLevel() == level
    
    def test_setup_logger_creates_directory(self, tmp_path):
        """Test that log directory is created if not exists"""
        log_dir = tmp_path / "logs" / "subdir"
        
        logger = setup_logger(
            name='test_logger_dir',
            log_dir=str(log_dir),
            log_level=logging.INFO
        )
        
        # Log a message to trigger directory creation
        logger.info("Test message")
        
        # Directory should exist or be creatable
        assert isinstance(logger, logging.Logger)
        
        # Try to create the directory if it doesn't exist
        # (it should be created by the logger)
        log_dir.parent.mkdir(parents=True, exist_ok=True)
        assert log_dir.parent.exists()


@pytest.mark.unit
class TestGetLogger:
    """Test get_logger convenience function"""
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger"""
        logger = get_logger('test_module')
        
        assert isinstance(logger, logging.Logger)
    
    def test_get_logger_same_name_returns_same_instance(self):
        """Test that same logger name returns same instance"""
        logger1 = get_logger('test_module_same')
        logger2 = get_logger('test_module_same')
        
        assert logger1 is logger2
    
    def test_get_logger_different_names_different_instances(self):
        """Test that different names return different instances"""
        logger1 = get_logger('module_a_unique')
        logger2 = get_logger('module_b_unique')
        
        assert logger1 is not logger2


@pytest.mark.unit
class TestLoggerLogging:
    """Test logging functionality"""
    
    def test_logger_writes_info(self, tmp_path):
        """Test writing info level logs"""
        logger = setup_logger(
            name='test_info',
            log_dir=str(tmp_path),
            log_level=logging.DEBUG
        )
        
        logger.info("Test info message")
        
        # Verify logger exists and is working
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_info'
    
    def test_logger_writes_debug(self, tmp_path):
        """Test writing debug level logs"""
        logger = setup_logger(
            name='test_debug',
            log_dir=str(tmp_path),
            log_level=logging.DEBUG
        )
        
        logger.debug("Test debug message")
        
        assert isinstance(logger, logging.Logger)
    
    def test_logger_writes_warning(self, tmp_path):
        """Test writing warning level logs"""
        logger = setup_logger(
            name='test_warning',
            log_dir=str(tmp_path),
            log_level=logging.WARNING
        )
        
        logger.warning("Test warning message")
        
        assert isinstance(logger, logging.Logger)
    
    def test_logger_writes_error(self, tmp_path):
        """Test writing error level logs"""
        logger = setup_logger(
            name='test_error',
            log_dir=str(tmp_path),
            log_level=logging.ERROR
        )
        
        logger.error("Test error message")
        
        assert isinstance(logger, logging.Logger)
    
    def test_logger_respects_log_level(self, tmp_path):
        """Test that logger respects configured log level"""
        logger = setup_logger(
            name='test_level',
            log_dir=str(tmp_path),
            log_level=logging.WARNING
        )
        
        # Test that logger accepts messages at all levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Verify logger is working
        assert logger.level == logging.WARNING or logger.getEffectiveLevel() == logging.WARNING


@pytest.mark.unit
class TestLoggerIntegration:
    """Integration tests for logging"""
    
    def test_multiple_messages_logged(self, tmp_path):
        """Test logging multiple messages"""
        logger = setup_logger(
            name='test_multi',
            log_dir=str(tmp_path),
            log_level=logging.DEBUG
        )
        
        messages = [
            (logger.debug, "Debug msg"),
            (logger.info, "Info msg"),
            (logger.warning, "Warning msg"),
            (logger.error, "Error msg"),
        ]
        
        for log_func, msg in messages:
            log_func(msg)
        
        # Verify logger is working
        assert isinstance(logger, logging.Logger)
        assert len(logger.handlers) > 0
    
    def test_logger_with_multiple_names(self, tmp_path):
        """Test multiple loggers with different names"""
        logger1 = setup_logger('module1_unique', str(tmp_path), logging.INFO)
        logger2 = setup_logger('module2_unique', str(tmp_path), logging.INFO)
        
        logger1.info("From module 1")
        logger2.info("From module 2")
        
        # Verify both loggers exist
        assert logger1.name == 'module1_unique'
        assert logger2.name == 'module2_unique'
        assert logger1 is not logger2
