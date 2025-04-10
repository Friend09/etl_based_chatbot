"""
Utility module providing specialized loggers for different application components.
"""

import os
import logging
import sys
import time  # Add missing import for time module
from pathlib import Path
import functools
from config.logging_config import (
    get_logger,
    set_log_level,
    log_function_call,
    ETL_LOG_FILE,
    WEB_LOG_FILE,
    DB_LOG_FILE,
    DEFAULT_LOG_LEVEL,
    LOG_LEVELS
)

class LoggerFactory:
    """Factory class to create and manage specialized loggers."""

    _loggers = {}

    @classmethod
    def get_etl_logger(cls, name=None):
        """Get a logger for ETL components."""
        logger_name = f"etl.{name}" if name else "etl"
        if logger_name not in cls._loggers:
            cls._loggers[logger_name] = get_logger(
                logger_name,
                log_file=ETL_LOG_FILE,
                console=True
            )
        return cls._loggers[logger_name]

    @classmethod
    def get_web_logger(cls, name=None):
        """Get a logger for web application components."""
        logger_name = f"web.{name}" if name else "web"
        if logger_name not in cls._loggers:
            cls._loggers[logger_name] = get_logger(
                logger_name,
                log_file=WEB_LOG_FILE,
                console=True
            )
        return cls._loggers[logger_name]

    @classmethod
    def get_db_logger(cls, name=None):
        """Get a logger for database components."""
        logger_name = f"db.{name}" if name else "db"
        if logger_name not in cls._loggers:
            cls._loggers[logger_name] = get_logger(
                logger_name,
                log_file=DB_LOG_FILE,
                console=True
            )
        return cls._loggers[logger_name]

    @classmethod
    def set_global_log_level(cls, level):
        """Set log level for all managed loggers."""
        for logger in cls._loggers.values():
            set_log_level(logger, level)

    @classmethod
    def set_environment(cls, environment):
        """Set log levels based on environment."""
        level = LOG_LEVELS.get(environment, DEFAULT_LOG_LEVEL)
        cls.set_global_log_level(level)


# Utility function to get a component logger
def get_component_logger(component_type, name=None):
    """
    Get an appropriate logger based on component type.

    Args:
        component_type (str): Type of component ('etl', 'web', or 'db')
        name (str, optional): Specific name within the component

    Returns:
        logging.Logger: Configured logger for the component
    """
    if component_type.lower() == 'etl':
        return LoggerFactory.get_etl_logger(name)
    elif component_type.lower() == 'web':
        return LoggerFactory.get_web_logger(name)
    elif component_type.lower() == 'db':
        return LoggerFactory.get_db_logger(name)
    else:
        # Default to app-level logger
        return get_logger(f"app.{name}" if name else "app")


# Decorators for logging within specific components
def log_etl_function(func=None, *, logger_name=None):
    """Decorator for logging ETL function calls."""
    def decorator(func):
        logger = LoggerFactory.get_etl_logger(logger_name or func.__module__)
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Starting {func.__name__}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"Completed {func.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {elapsed:.2f}s: {str(e)}")
                raise
        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def log_web_function(func=None, *, logger_name=None):
    """Decorator for logging web function calls."""
    def decorator(func):
        logger = LoggerFactory.get_web_logger(logger_name or func.__name__)
        return log_function_call(logger)(func)

    if func is None:
        return decorator
    return decorator(func)


def log_db_function(func=None):
    """
    Decorator for database functions.

    Usage:
        @log_db_function
        def my_db_function():
            pass
    """
    logger = get_component_logger('db')

    if func is None:
        return lambda f: log_function_call(f, logger=logger)

    return log_function_call(func, logger=logger)


# Structured logging support
def log_structured(logger, level, event, **kwargs):
    """
    Log a structured message for potential integration with log aggregation systems.

    Args:
        logger (logging.Logger): Logger to use
        level (str): Log level ('debug', 'info', 'warning', 'error', 'critical')
        event (str): Event name or type
        **kwargs: Additional structured data to include
    """
    # Create a structured log message
    message = {
        "event": event,
        "data": kwargs
    }

    # Get the appropriate logging method
    log_method = getattr(logger, level.lower(), logger.info)

    # Log the structured message
    log_method(f"STRUCTURED_LOG: {message}")


def setup_logger(name: str, log_level: int = logging.INFO, log_file: str = None):
    """
    Sets up and returns a logger with specified configuration.

    Args:
        name: Name of the logger
        log_level: Logging level (default: INFO)
        log_file: Optional path to log file

    Returns:
        configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler if log_file is specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file).parent
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_function_call(func=None, logger=None):
    """
    Decorator to log function calls with timing information.

    Args:
        func: The function to decorate (when used as @log_function_call)
        logger: Optional logger to use (when used as @log_function_call(logger=logger))

    Usage:
        @log_function_call
        def my_func():
            pass

        # or with specific logger:
        @log_function_call(logger=my_logger)
        def my_func():
            pass
    """
    def decorator(f):
        _logger = logger or get_component_logger(f.__module__.split('.')[0])

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            _logger.debug(f"Starting {f.__name__}")
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                elapsed = time.time() - start_time
                _logger.debug(f"Completed {f.__name__} in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                _logger.error(f"Error in {f.__name__} after {elapsed:.2f}s: {str(e)}")
                raise
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
