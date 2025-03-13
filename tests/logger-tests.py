"""
Unit tests for the logging system.
"""

import os
import unittest
import logging
import tempfile
import json
import re
from pathlib import Path

# Import logging components to test
from config.logging_config import (
    get_logger, 
    SensitiveInfoFilter, 
    get_file_handler,
    get_console_handler,
    SENSITIVE_PATTERNS
)
from utils import (
    get_component_logger,
    log_etl_function,
    log_structured,
    LoggerFactory
)

class TestLoggingConfig(unittest.TestCase):
    """Test the logging configuration module."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary log file
        self.temp_log_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_log_file.close()
        
        # Reset LoggerFactory
        LoggerFactory._loggers = {}
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary log file
        os.unlink(self.temp_log_file.name)
    
    def test_file_handler_creation(self):
        """Test creation of file handler."""
        handler = get_file_handler(self.temp_log_file.name)
        self.assertIsInstance(handler, logging.handlers.RotatingFileHandler)
        self.assertEqual(handler.baseFilename, self.temp_log_file.name)
    
    def test_console_handler_creation(self):
        """Test creation of console handler."""
        handler = get_console_handler()
        self.assertIsInstance(handler, logging.StreamHandler)
    
    def test_get_logger(self):
        """Test getting a configured logger."""
        logger = get_logger("test_logger", self.temp_log_file.name)
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(len(logger.handlers), 2)  # File and console handlers
    
    def test_sensitive_info_filtering(self):
        """Test filtering of sensitive information."""
        # Create a filter
        sensitive_filter = SensitiveInfoFilter()
        
        # Create a record with sensitive information
        record = logging.LogRecord(
            name="test", 
            level=logging.INFO, 
            pathname="", 
            lineno=0, 
            msg="api_key='secret12345' and password='my_password'", 
            args=(), 
            exc_info=None
        )
        
        # Apply filter
        sensitive_filter.filter(record)
        
        # Check that sensitive info was masked
        self.assertNotIn("secret12345", record.msg)
        self.assertNotIn("my_password", record.msg)
        self.assertIn("api_key=*****", record.msg)
        self.assertIn("password=*****", record.msg)
        
    def test_sensitive_patterns(self):
        """Test regex patterns for sensitive data masking."""
        sensitive_text = "api_key='abcd1234', token=\"xyz789\", password = 'secret'"
        
        for pattern, replacement in SENSITIVE_PATTERNS:
            sensitive_text = re.sub(pattern, replacement, sensitive_text)
        
        # Check that all sensitive info was masked
        self.assertNotIn("abcd1234", sensitive_text)
        self.assertNotIn("xyz789", sensitive_text)
        self.assertNotIn("secret", sensitive_text)
        self.assertIn("api_key=*****", sensitive_text)
        self.assertIn("token=*****", sensitive_text)
        self.assertIn("password=*****", sensitive_text)


class TestLoggerUtilities(unittest.TestCase):
    """Test the logger utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary log directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create ETL log file path
        self.etl_log_file = Path(self.temp_dir.name) / "etl.log"
        
        # Reset LoggerFactory
        LoggerFactory._loggers = {}
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and files
        self.temp_dir.cleanup()
    
    def test_get_component_logger(self):
        """Test getting component-specific loggers."""
        # Get loggers for different components
        etl_logger = get_component_logger('etl', 'test')
        web_logger = get_component_logger('web', 'test')
        db_logger = get_component_logger('db', 'test')
        
        # Check logger names
        self.assertEqual(etl_logger.name, "etl.test")
        self.assertEqual(web_logger.name, "web.test")
        self.assertEqual(db_logger.name, "db.test")
        
        # Check singleton behavior from LoggerFactory
        etl_logger2 = get_component_logger('etl', 'test')
        self.assertIs(etl_logger, etl_logger2)
    
    def test_log_function_decorator(self):
        """Test the function logging decorator."""
        # Define a test function with the decorator
        @log_etl_function
        def test_function(arg1, arg2=None):
            return arg1 + (arg2 or 0)
        
        # Call the function and check result
        result = test_function(1, 2)
        self.assertEqual(result, 3)
        
        # We can't easily check the log output in unit tests,
        # but we can verify the function still works correctly
        
    def test_log_structured(self):
        """Test structured logging."""
        # Create a file logger
        logger = get_logger("test_structured", self.etl_log_file)
        
        # Log a structured message
        log_structured(
            logger,
            "info",
            "test_event",
            param1="value1",
            param2=123
        )
        
        # Verify the log file exists
        self.assertTrue(self.etl_log_file.exists())
        
        # Read the log file content
        with open(self.etl_log_file, 'r') as f:
            log_content = f.read()
        
        # Check that the structured log message was written
        self.assertIn("STRUCTURED_LOG", log_content)
        self.assertIn("test_event", log_content)
        self.assertIn("value1", log_content)
        self.assertIn("123", log_content)


class TestLoggerIntegration(unittest.TestCase):
    """Integration tests for the logging system."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary log directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create log file paths
        self.etl_log_file = Path(self.temp_dir.name) / "etl.log"
        self.web_log_file = Path(self.temp_dir.name) / "web.log"
        
        # Reset LoggerFactory
        LoggerFactory._loggers = {}
        
        # Create a test class with logging
        class TestETLComponent:
            def __init__(self):
                self.logger = get_component_logger('etl', 'test_component')
                
            @log_etl_function
            def process_data(self, data, api_key=None):
                self.logger.info(f"Processing data: {data}")
                if api_key:
                    self.logger.debug(f"Using API key: {api_key}")
                return f"Processed: {data}"
        
        self.test_component = TestETLComponent()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and files
        self.temp_dir.cleanup()
    
    def test_log_sensitive_data(self):
        """Test logging with sensitive data."""
        # Process data with an API key
        self.test_component.process_data("test_data", api_key="secret123")
        
        # Wait a moment for logs to be written
        import time
        time.sleep(0.1)
        
        # Check that the log file exists
        self.assertTrue(Path(self.etl_log_file).exists())
        
        # Read the log file content
        with open(self.etl_log_file, 'r') as f:
            log_content = f.read()
        
        # Check that sensitive info was masked
        self.assertIn("Processing data: test_data", log_content)
        self.assertNotIn("secret123", log_content)
        self.assertIn("api_key=*****", log_content)


if __name__ == '__main__':
    unittest.main()
