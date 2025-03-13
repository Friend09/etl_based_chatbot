"""
Database package for the Weather ETL Chatbot application.
Provides database models and utilities.
"""

# Import commonly used database functions for easier access
from database.db_connector import DatabaseConnector, DatabaseConnectionError, DatabaseQueryError
from database.db_utils import (
    get_or_create_location,
    save_current_weather,
    save_forecast_data,
    generate_daily_weather_report,
    get_latest_weather
)

# Make these classes and functions available when importing the database package
__all__ = [
    'DatabaseConnector',
    'DatabaseConnectionError',
    'DatabaseQueryError',
    'get_or_create_location',
    'save_current_weather',
    'save_forecast_data',
    'generate_daily_weather_report',
    'get_latest_weather'
]
