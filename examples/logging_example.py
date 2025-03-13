"""
Example script demonstrating the usage of the logging system.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import logging components
from utils.logger import (
    setup_logger,
    get_component_logger,
    log_etl_function,
    log_web_function,
    log_db_function,
    log_structured,
    LoggerFactory
)

def demonstrate_basic_logging():
    """Demonstrate basic logging functionality."""
    print("\n=== Basic Logging ===")

    # Create a basic logger
    logger = setup_logger("example")

    # Log messages at different levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    print("Basic log messages have been written")

def demonstrate_component_loggers():
    """Demonstrate component-specific loggers."""
    print("\n=== Component Loggers ===")

    # Get loggers for different components
    etl_logger = get_component_logger('etl', 'example')
    web_logger = get_component_logger('web', 'example')
    db_logger = get_component_logger('db', 'example')

    # Log component-specific messages
    etl_logger.info("ETL component: Processing weather data")
    web_logger.info("Web component: Handling API request")
    db_logger.info("Database component: Executing query")

    print("Component-specific logs have been written")

def demonstrate_sensitive_data_masking():
    """Demonstrate masking of sensitive information."""
    print("\n=== Sensitive Data Masking ===")

    logger = setup_logger("security_example")

    # Log messages containing sensitive information
    logger.info("Connecting with api_key='1234secret5678'")
    logger.debug("Database password='secure_pwd123'")
    logger.warning("Auth token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'")
    logger.error("Credential='admin:s3cr3t' is invalid")

    print("Sensitive data has been logged (and should be masked)")

@log_etl_function
def process_weather_data(location, date, api_key=None):
    """Example ETL function with logging decorator."""
    logger = get_component_logger('etl', 'processor')

    logger.info(f"Processing weather data for {location} on {date}")

    if api_key:
        logger.debug(f"Using API key: {api_key}")

    # Simulate processing
    time.sleep(0.5)

    logger.info(f"Weather data processing completed for {location}")

    return {
        "location": location,
        "date": date,
        "temperature": 23.5,
        "humidity": 65
    }

def demonstrate_function_decorators():
    """Demonstrate function logging decorators."""
    print("\n=== Function Logging Decorators ===")

    # Call function with decorator
    result = process_weather_data(
        "New York",
        "2025-03-13",
        api_key="secret_key_1234"
    )

    print(f"Function returned: {result}")
    print("Function entry/exit has been logged")

def demonstrate_structured_logging():
    """Demonstrate structured logging."""
    print("\n=== Structured Logging ===")

    # Get a logger
    logger = get_component_logger('web', 'api')

    # Log structured events
    log_structured(
        logger,
        "info",
        "api_request",
        endpoint="/weather",
        method="GET",
        params={"location": "New York"},
        status_code=200,
        response_time=0.25
    )

    log_structured(
        logger,
        "error",
        "api_error",
        endpoint="/forecast",
        method="POST",
        error_code=500,
        error_message="Internal server error"
    )

    print("Structured logs have been written")

def demonstrate_environment_based_logging():
    """Demonstrate environment-based log levels."""
    print("\n=== Environment-Based Logging ===")

    # Get current environment
    current_env = os.getenv("APP_ENV", "development")
    print(f"Current environment: {current_env}")

    # Test with different environments
    environments = ["development", "testing", "production"]

    for env in environments:
        # Set environment variable
        os.environ["APP_ENV"] = env

        # Re-initialize loggers to pick up new environment
        LoggerFactory._loggers = {}

        # Get a logger
        logger = get_component_logger('app', env)

        # Log at all levels
        logger.debug(f"[{env}] Debug message")
        logger.info(f"[{env}] Info message")
        logger.warning(f"[{env}] Warning message")
        logger.error(f"[{env}] Error message")

        print(f"Logs for {env} environment have been written")

    # Restore original environment
    os.environ["APP_ENV"] = current_env

def main():
    """Run all logging demonstrations."""
    print("=== Logging System Examples ===")

    # Run demonstrations
    demonstrate_basic_logging()
    demonstrate_component_loggers()
    demonstrate_sensitive_data_masking()
    demonstrate_function_decorators()
    demonstrate_structured_logging()
    demonstrate_environment_based_logging()

    print("\nAll logging examples completed. Check the log files in the 'logs' directory.")

if __name__ == "__main__":
    main()
