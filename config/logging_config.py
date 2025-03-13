"""
Logging configuration module.

This module provides functions to configure the logging system for the application.
"""

import logging.config
import os
import functools
from pathlib import Path

# Import and re-export constants
from .logging_constants import (
    DEFAULT_LOG_LEVEL, LOG_LEVELS,
    LOG_DIR, ETL_LOG_FILE, WEB_LOG_FILE, DB_LOG_FILE
)

# Make constants available for import from this module
__all__ = [
    'DEFAULT_LOG_LEVEL', 'LOG_LEVELS', 'LOG_DIR',
    'ETL_LOG_FILE', 'WEB_LOG_FILE', 'DB_LOG_FILE',
    'configure_logging', 'get_logger', 'set_log_level', 'log_function_call'
]

def configure_logging(log_dir="logs", level=logging.INFO):
    """
    Configure the logging system with detailed settings.

    Args:
        log_dir: Directory to store logs
        level: Default logging level

    Returns:
        None
    """
    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Define logging configuration
    config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.DEBUG,
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'application.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': logging.ERROR,
                'formatter': 'detailed',
                'filename': os.path.join(log_dir, 'errors.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'error_file'],
                'level': logging.DEBUG,
                'propagate': True
            }
        }
    }

    # Apply configuration
    logging.config.dictConfig(config)
    logging.info("Logging system configured")

    return logging.getLogger()

def get_logger(name, log_file=None, console=True, level=None):
    """
    Get a configured logger instance.

    Args:
        name: Logger name
        log_file: Optional log file path
        console: Whether to log to console
        level: Log level (defaults to DEFAULT_LOG_LEVEL)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if handlers aren't already set up
    if not logger.handlers:
        # Set level (from param or env or default)
        level = level or os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL)
        if isinstance(level, str):
            level = LOG_LEVELS.get(level.lower(), DEFAULT_LOG_LEVEL)

        logger.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add console handler if requested
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # Add file handler if specified
        if log_file:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            Path(log_dir).mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

def set_log_level(logger, level):
    """
    Set log level for a logger and all its handlers.

    Args:
        logger: Logger to modify
        level: New log level
    """
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.lower(), DEFAULT_LOG_LEVEL)

    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)

def log_function_call(logger):
    """
    Decorator factory for logging function calls.

    Args:
        logger: Logger to use for logging

    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator
