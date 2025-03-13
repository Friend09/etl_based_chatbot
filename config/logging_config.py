"""
Logging configuration for the Weather ETL Chatbot application.
Sets up logging handlers and formatters for different components.
"""

import os
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from config.settings import LOG_DIR

def configure_logging(name="weather_etl_chatbot", log_to_console=True):
    """
    Configure application logging with file and optional console output.

    Args:
        name (str): Logger name, used for the log file name
        log_to_console (bool): Whether to log to console as well as file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create file handler for general logs (rotate by size)
    log_file = os.path.join(LOG_DIR, f"{name}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Create file handler for errors (rotate daily)
    error_log_file = os.path.join(LOG_DIR, f"{name}_error.log")
    error_file_handler = TimedRotatingFileHandler(
        error_log_file,
        when="midnight",
        interval=1,
        backupCount=30
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)

    # Optionally add console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def get_component_logger(component_name, parent_logger="weather_etl_chatbot"):
    """
    Get a logger for a specific component, inheriting parent logger settings.

    Args:
        component_name (str): Component name (etl, web, etc.)
        parent_logger (str): Parent logger name

    Returns:
        logging.Logger: Component-specific logger
    """
    logger_name = f"{parent_logger}.{component_name}"
    return logging.getLogger(logger_name)

def configure_all_loggers():
    """
    Configure all application loggers.
    This can be called from the main application entry point.
    """
    # Configure root logger
    root_logger = configure_logging("weather_etl_chatbot")

    # Configure component-specific loggers
    components = ["etl", "web", "database"]
    for component in components:
        get_component_logger(component)

    return root_logger
