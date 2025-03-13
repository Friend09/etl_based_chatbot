"""
Logging configuration module.

This module provides functions to configure the logging system for the application.
"""

import sys
import logging
import logging.config
import logging.handlers
import os
import functools
from pathlib import Path

from config.settings import LOG_LEVEL, LOG_DIR

# Constants for logging
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5  # Keep 5 backup files

# Map string log levels to logging constants
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

DEFAULT_LOG_LEVEL = logging.INFO

# Make sure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

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

def log_function_call(func_or_logger=None):
    """
    Decorator for logging function calls.

    Can be used in two ways:
    1. As a direct decorator: @log_function_call
    2. With a logger: @log_function_call(logger)

    Args:
        func_or_logger: Function to decorate or logger to use

    Returns:
        Wrapped function or decorator function
    """
    if func_or_logger is None or isinstance(func_or_logger, logging.Logger):
        # Case 2: Called with logger or no args
        logger = func_or_logger or logging.getLogger()

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
    else:
        # Case 1: Called as direct decorator
        func = func_or_logger
        logger = logging.getLogger(func.__module__)

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

def get_log_level(level_name=None):
    """
    Get the log level from a string.

    Args:
        level_name (str, optional): Log level name (DEBUG, INFO, etc.).
            If None, will use LOG_LEVEL from settings.

    Returns:
        int: The log level constant (e.g., logging.INFO)
    """
    if level_name is None:
        level_name = LOG_LEVEL

    level_name = level_name.upper()

    # Map string log levels to logging constants
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    return log_levels.get(level_name, logging.INFO)

def create_log_formatter(detailed=False):
    """
    Create a log formatter.

    Args:
        detailed (bool): Whether to use detailed format.
            Detailed format includes filename, line number, and function name.

    Returns:
        logging.Formatter: A log formatter
    """
    log_format = DETAILED_LOG_FORMAT if detailed else DEFAULT_LOG_FORMAT
    return logging.Formatter(log_format)

def create_file_handler(log_file, level=None, formatter=None):
    """
    Create a rotating file handler for logging.

    Args:
        log_file (str): Path to the log file.
        level (int, optional): Log level. If None, will use level from settings.
        formatter (logging.Formatter, optional): Log formatter.
            If None, will create a default formatter.

    Returns:
        logging.Handler: A file handler for logging
    """
    if level is None:
        level = get_log_level()

    if formatter is None:
        formatter = create_log_formatter()

    # Create directory for log file if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )

    handler.setLevel(level)
    handler.setFormatter(formatter)

    return handler

def create_console_handler(level=None, formatter=None):
    """
    Create a console handler for logging.

    Args:
        level (int, optional): Log level. If None, will use level from settings.
        formatter (logging.Formatter, optional): Log formatter.
            If None, will create a default formatter.

    Returns:
        logging.Handler: A console handler for logging
    """
    if level is None:
        level = get_log_level()

    if formatter is None:
        formatter = create_log_formatter()

    # Create a console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    return handler

def configure_logger(logger, level=None, add_console_handler=True,
                    log_file=None, detailed=False):
    """
    Configure a logger with handlers and formatters.

    Args:
        logger (logging.Logger): The logger to configure.
        level (int, optional): Log level. If None, will use level from settings.
        add_console_handler (bool): Whether to add a console handler.
        log_file (str, optional): Path to the log file.
            If None, no file handler will be added.
        detailed (bool): Whether to use detailed format.

    Returns:
        logging.Logger: The configured logger
    """
    if level is None:
        level = get_log_level()

    # Set the logger's level
    logger.setLevel(level)

    # Remove any existing handlers to avoid duplicates
    while logger.handlers:
        logger.removeHandler(logger.handlers[0])

    # Create formatter
    formatter = create_log_formatter(detailed=detailed)

    # Add console handler if requested
    if add_console_handler:
        console_handler = create_console_handler(level=level, formatter=formatter)
        logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        file_handler = create_file_handler(log_file, level=level, formatter=formatter)
        logger.addHandler(file_handler)

    # Don't propagate to root logger if this is not the root logger
    if logger.name != 'root':
        logger.propagate = False

    return logger

def get_component_logger(component, subcomponent=None, level=None,
                        add_console_handler=True, detailed=False):
    """
    Get a logger for a specific component.

    Args:
        component (str): The component name (e.g., 'etl', 'web').
        subcomponent (str, optional): The subcomponent name (e.g., 'extractor').
        level (int, optional): Log level. If None, will use level from settings.
        add_console_handler (bool): Whether to add a console handler.
        detailed (bool): Whether to use detailed format.

    Returns:
        logging.Logger: The configured logger
    """
    # Construct logger name
    logger_name = component
    if subcomponent:
        logger_name = f"{component}.{subcomponent}"

    # Get or create the logger
    logger = logging.getLogger(logger_name)

    # Determine log file based on component
    log_file = os.path.join(LOG_DIR, f"{component}.log")

    # Configure the logger
    configure_logger(
        logger,
        level=level,
        add_console_handler=add_console_handler,
        log_file=log_file,
        detailed=detailed
    )

    return logger

def configure_root_logger():
    """
    Configure the root logger for the application.

    Returns:
        logging.Logger: The configured root logger
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Configure with both console and file handlers
    log_file = os.path.join(LOG_DIR, 'app.log')
    configure_logger(
        root_logger,
        level=get_log_level(),
        add_console_handler=True,
        log_file=log_file,
        detailed=True
    )

    root_logger.info("Root logger configured")
    return root_logger
