"""
Test module for the logging system.
"""

import unittest
import logging
import os
import tempfile
from pathlib import Path

from utils.logger import (
    setup_logger,
    get_component_logger,
    log_etl_function,
    log_web_function,
    log_db_function,
    log_structured,
    LoggerFactory
)

class TestLogging(unittest.TestCase):
    """Test case for logging functionality."""

    def setUp(self):
        # Create a temporary log directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = Path(self.temp_dir.name)

        # Reset LoggerFactory
        LoggerFactory._loggers = {}

    def tearDown(self):
        # Clean up temporary directory
        self.temp_dir.cleanup()

    def test_setup_logger(self):
        """Test that setup_logger creates a logger correctly."""
        logger = setup_logger("test", log_level=logging.DEBUG)

        self.assertEqual(logger.name, "test")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertTrue(len(logger.handlers) > 0)

    def test_setup_logger_with_file(self):
        """Test setup_logger with a log file."""
        log_file = self.log_dir / "test.log"
        logger = setup_logger("test_file", log_level=logging.INFO, log_file=log_file)

        logger.info("Test message")

        self.assertTrue(log_file.exists())
        with open(log_file, 'r') as f:
            self.assertIn("Test message", f.read())

    def test_component_logger_etl(self):
        """Test ETL component logger."""
        logger = get_component_logger("etl", "test_component")
        self.assertEqual(logger.name, "etl.test_component")

    def test_component_logger_web(self):
        """Test web component logger."""
        logger = get_component_logger("web", "test_component")
        self.assertEqual(logger.name, "web.test_component")

    def test_component_logger_db(self):
        """Test db component logger."""
        logger = get_component_logger("db", "test_component")
        self.assertEqual(logger.name, "db.test_component")

    @log_etl_function
    def sample_etl_function(self, value):
        """Sample ETL function for testing the decorator."""
        return value * 2

    def test_log_etl_function_decorator(self):
        """Test the ETL function logging decorator."""
        result = self.sample_etl_function(5)
        self.assertEqual(result, 10)

    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = setup_logger("structured_test")

        # Temporarily capture log output
        with self.assertLogs(logger=logger, level='INFO') as log_context:
            log_structured(logger, "info", "test_event", param1="value1", param2=123)

            # Check log output
            self.assertEqual(len(log_context.records), 1)
            self.assertIn("STRUCTURED_LOG:", log_context.records[0].message)
            self.assertIn("test_event", log_context.records[0].message)
            self.assertIn("value1", log_context.records[0].message)

if __name__ == "__main__":
    unittest.main()
