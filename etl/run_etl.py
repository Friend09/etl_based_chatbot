"""
Script to run the ETL process for weather data collection.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import json

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from etl.weather_collector import WeatherCollector
from database.db_connector import DatabaseConnector
from utils.logger import get_component_logger

# Configure logger
logger = get_component_logger('etl', 'run_etl')

def run_etl():
    """Run the ETL process to collect and store weather data."""
    try:
        logger.info("Starting ETL process")

        # Initialize weather collector
        collector = WeatherCollector()

        # Fetch current weather
        logger.info("Fetching current weather data")
        current_weather = collector.fetch_current_weather()
        processed_current = collector.process_current_weather(current_weather)

        # Fetch forecast
        logger.info("Fetching forecast data")
        forecast = collector.fetch_forecast()
        processed_forecast = collector.process_forecast(forecast)

        # Initialize database connection
        db = DatabaseConnector()

        # Save current weather to database
        logger.info("Saving current weather data to database")
        with db.transaction() as cursor:
            # First, ensure the location exists
            cursor.execute("""
                INSERT INTO locations (city_name, country, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (city_name, country) DO NOTHING
                RETURNING location_id
            """, (collector.city, 'US', collector.lat, collector.lon))

            result = cursor.fetchone()
            if result:
                location_id = result[0]
            else:
                cursor.execute("""
                    SELECT location_id FROM locations
                    WHERE city_name = %s AND country = %s
                """, (collector.city, 'US'))
                location_id = cursor.fetchone()[0]

            # Insert current weather data
            cursor.execute("""
                INSERT INTO weather_current (
                    location_id, timestamp, temperature, feels_like,
                    humidity, pressure, wind_speed, weather_condition,
                    weather_description, raw_data
                ) VALUES (
                    %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                location_id,
                processed_current['temperature'],
                processed_current['feels_like'],
                processed_current['humidity'],
                processed_current['pressure'],
                processed_current['wind_speed'],
                processed_current['weather_main'],
                processed_current['weather_description'],
                json.dumps(processed_current['raw_data'])
            ))

        logger.info("ETL process completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error in ETL process: {str(e)}")
        return False

if __name__ == "__main__":
    run_etl()
