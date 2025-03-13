"""
Utility package for the weather ETL and chatbot application.
"""

import os
from pathlib import Path

# Create the utils directory if it doesn't exist
utils_dir = Path(__file__).parent
utils_dir.mkdir(exist_ok=True)

# Ensure the logs directory exists
logs_dir = utils_dir.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Import logger utilities for easy access
from utils.logger import (
    get_component_logger,
    log_etl_function,
    log_web_function,
    log_db_function,
    log_structured,
    LoggerFactory
)

from .logger import setup_logger

__all__ = [
    'get_component_logger',
    'log_etl_function',
    'log_web_function',
    'log_db_function',
    'log_structured',
    'LoggerFactory'
]
