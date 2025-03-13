#!/usr/bin/env python3
"""
Tests for database connectivity and functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_connector import DatabaseConnector
from database.db_utils import get_value_from_result
from utils.logger import get_component_logger

# Set up logger
logger = get_component_logger('test', 'database')

def test_database_connection():
    """Test database connection and run a simple query."""
    db = DatabaseConnector()

    try:
        logger.info("Testing database connection...")

        # Try to get database version
        query = "SELECT version();"
        result = db.execute_query(query)

        if result:
            # Extract version safely using our helper function
            version = None
            if isinstance(result[0], dict):
                version = result[0].get('version')
            elif isinstance(result[0], (list, tuple)):
                version = result[0][0] if result[0] else None
            else:
                version = str(result[0])

            if version:
                logger.info(f"Successfully connected to database. PostgreSQL version: {version}")
                print(f"Database connection successful! PostgreSQL version: {version}")
            else:
                logger.info(f"Successfully connected to database. Result: {result[0]}")
                print(f"Database connection successful! Result: {result[0]}")

            # Check if tables exist
            tables_query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """

            tables = db.execute_query(tables_query)

            if tables:
                logger.info(f"Found {len(tables)} tables in the database:")
                print(f"\nFound {len(tables)} tables in the database:")

                for i, table_row in enumerate(tables):
                    # Extract table name safely
                    table_name = None
                    if isinstance(table_row, dict):
                        table_name = table_row.get('table_name')
                    elif isinstance(table_row, (list, tuple)):
                        table_name = table_row[0] if table_row else None
                    else:
                        table_name = str(table_row)

                    print(f"{i+1}. {table_name}")
            else:
                logger.warning("No tables found in the database.")
                print("\nNo tables found in the database.")

            return True
        else:
            logger.error("Connection test failed: No result returned")
            print("Database connection test failed! No result returned.")
            return False

    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        print(f"Database connection test failed! Error: {str(e)}")
        return False

def test_table_contents():
    """Test retrieving data from tables to verify database content."""
    db = DatabaseConnector()

    try:
        logger.info("Checking database content...")

        # Check locations table
        loc_query = "SELECT COUNT(*) FROM locations"
        result = db.execute_query(loc_query)

        if result:
            count = None
            if isinstance(result[0], dict):
                count = result[0].get('count')
            elif isinstance(result[0], (list, tuple)):
                count = result[0][0] if result[0] else 0

            print(f"\nLocations table contains {count} records")

            # Get a sample of locations
            if count and int(count) > 0:
                sample_query = "SELECT location_id, city_name, country FROM locations LIMIT 5"
                samples = db.execute_query(sample_query)

                print("\nSample locations:")
                for i, loc in enumerate(samples):
                    loc_id = get_value_from_result(loc, 'location_id', get_value_from_result(loc, 0))
                    city = get_value_from_result(loc, 'city_name', get_value_from_result(loc, 1))
                    country = get_value_from_result(loc, 'country', get_value_from_result(loc, 2))
                    print(f"  {i+1}. ID: {loc_id}, {city}, {country}")

        # Check weather_current table
        weather_query = "SELECT COUNT(*) FROM weather_current"
        result = db.execute_query(weather_query)

        if result:
            count = None
            if isinstance(result[0], dict):
                count = result[0].get('count')
            elif isinstance(result[0], (list, tuple)):
                count = result[0][0] if result[0] else 0

            print(f"\nWeather_current table contains {count} records")

            # Get the latest weather record
            if count and int(count) > 0:
                latest_query = """
                    SELECT wc.weather_id, wc.timestamp, wc.temperature,
                           l.city_name, l.country
                    FROM weather_current wc
                    JOIN locations l ON wc.location_id = l.location_id
                    ORDER BY wc.timestamp DESC
                    LIMIT 1
                """
                latest = db.execute_query(latest_query)

                if latest:
                    record = latest[0]
                    weather_id = get_value_from_result(record, 'weather_id', get_value_from_result(record, 0))
                    timestamp = get_value_from_result(record, 'timestamp', get_value_from_result(record, 1))
                    temp = get_value_from_result(record, 'temperature', get_value_from_result(record, 2))
                    city = get_value_from_result(record, 'city_name', get_value_from_result(record, 3))
                    country = get_value_from_result(record, 'country', get_value_from_result(record, 4))

                    print(f"\nLatest weather record:")
                    print(f"  ID: {weather_id}")
                    print(f"  Location: {city}, {country}")
                    print(f"  Timestamp: {timestamp}")
                    print(f"  Temperature: {temp}°C")

        # Check forecast table
        forecast_query = "SELECT COUNT(*) FROM weather_forecast"
        result = db.execute_query(forecast_query)

        if result:
            count = None
            if isinstance(result[0], dict):
                count = result[0].get('count')
            elif isinstance(result[0], (list, tuple)):
                count = result[0][0] if result[0] else 0

            print(f"\nWeather_forecast table contains {count} records")

        return True

    except Exception as e:
        logger.error(f"Error checking database content: {str(e)}")
        print(f"Error checking database content: {str(e)}")
        return False

def main():
    """Run the database tests."""
    print("\n=== Database Connectivity Test ===\n")
    connection_success = test_database_connection()

    if connection_success:
        print("\n=== Database Content Test ===\n")
        test_table_contents()

    return connection_success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
