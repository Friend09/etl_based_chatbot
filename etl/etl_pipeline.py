#!/usr/bin/env python3
"""
Main ETL pipeline for collecting, transforming, and loading weather data.
Orchestrates the ETL process from data collection to database insertion.
"""

import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl.weather_collector import (
    get_current_weather,
    get_forecast,
    save_weather_data,
    APIError
)
from database.db_utils import (
    get_or_create_location,
    save_current_weather,
    save_forecast_data,
    generate_daily_weather_report
)
from utils.logger import get_component_logger, log_etl_function

# Set up logger
logger = get_component_logger('etl', 'pipeline')

# Constants
DEFAULT_CITY = "Louisville,KY,US"
DEFAULT_COUNTRY = "US"
DEFAULT_FORECAST_DAYS = 5

class ETLPipeline:
    """Main ETL pipeline for weather data."""

    def __init__(self, city=None, country=None, forecast_days=DEFAULT_FORECAST_DAYS):
        """
        Initialize the ETL pipeline.

        Args:
            city (str, optional): City name for weather data
            country (str, optional): Country code for the city
            forecast_days (int, optional): Number of forecast days to collect
        """
        # Use environment variables if available, otherwise use defaults
        self.city = city or os.environ.get("WEATHER_CITY", DEFAULT_CITY)
        self.country = country or os.environ.get("WEATHER_COUNTRY", DEFAULT_COUNTRY)
        self.forecast_days = forecast_days

        logger.info(f"ETL Pipeline initialized for {self.city}")

    @log_etl_function
    def extract(self):
        """
        Extract weather data from API.

        Returns:
            tuple: (current_weather, forecast)
        """
        logger.info(f"Starting data extraction for {self.city}")

        try:
            # Get current weather
            current_weather = get_current_weather(self.city)
            logger.info("Successfully extracted current weather data")

            # Get forecast data
            forecast = get_forecast(self.city, days=self.forecast_days)
            logger.info(f"Successfully extracted {self.forecast_days}-day forecast data")

            return current_weather, forecast

        except APIError as e:
            logger.error(f"API error during extraction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {str(e)}")
            raise

    @log_etl_function
    def transform(self, current_weather, forecast):
        """
        Transform the raw weather data.

        Args:
            current_weather (dict): Current weather data
            forecast (dict): Forecast data

        Returns:
            tuple: (processed_current, processed_forecast)
        """
        logger.info("Starting data transformation")

        # For now, we're using the raw data as is
        # In a more complex implementation, we might apply more transformations

        return current_weather, forecast

    @log_etl_function
    def load(self, current_weather, forecast):
        """
        Load processed data into database.

        Args:
            current_weather (dict): Processed current weather data
            forecast (dict): Processed forecast data

        Returns:
            tuple: (current_id, forecast_ids)
        """
        logger.info("Starting data loading to database")

        try:
            # Save current weather to database
            current_id = save_current_weather(current_weather)
            logger.info(f"Successfully loaded current weather data (ID: {current_id})")

            # Save forecast to database
            forecast_ids = save_forecast_data(forecast)
            logger.info(f"Successfully loaded {len(forecast_ids)} forecast records")

            return current_id, forecast_ids

        except Exception as e:
            logger.error(f"Error during data loading: {str(e)}")
            raise

    @log_etl_function
    def backup_to_files(self, current_weather, forecast):
        """
        Backup data to files.

        Args:
            current_weather (dict): Current weather data
            forecast (dict): Forecast data
        """
        try:
            # Generate filenames with timestamp
            date_str = datetime.now().strftime('%Y%m%d')

            # Save to JSON files
            current_path = save_weather_data(
                current_weather,
                filename=f"current_{date_str}.json"
            )

            forecast_path = save_weather_data(
                forecast,
                filename=f"forecast_{date_str}.json"
            )

            logger.info(f"Backed up current weather to {current_path}")
            logger.info(f"Backed up forecast to {forecast_path}")

        except Exception as e:
            logger.warning(f"Error during file backup: {str(e)}")
            # Don't fail the pipeline if backups fail

    @log_etl_function
    def run(self):
        """
        Run the complete ETL pipeline.

        Returns:
            bool: Success status
        """
        start_time = time.time()
        logger.info(f"Starting ETL pipeline for {self.city}")

        try:
            # Extract data
            current_weather, forecast = self.extract()

            # Transform data
            processed_current, processed_forecast = self.transform(current_weather, forecast)

            # Backup data to files
            self.backup_to_files(processed_current, processed_forecast)

            # Load data to database
            current_id, forecast_ids = self.load(processed_current, processed_forecast)

            # Generate daily report
            try:
                # Extract location_id from the weather_id
                query = """
                SELECT location_id FROM weather_current WHERE weather_id = %s
                """
                from database.db_connector import DatabaseConnector
                db = DatabaseConnector()
                result = db.execute_query(query, (current_id,))

                if result:
                    location_id = result[0][0] if isinstance(result[0], tuple) else result[0]['location_id']
                    report_id = generate_daily_weather_report(location_id)
                    if report_id:
                        logger.info(f"Generated daily weather report (ID: {report_id})")
            except Exception as e:
                logger.warning(f"Error generating daily report: {str(e)}")

            # Calculate and log pipeline metrics
            elapsed_time = time.time() - start_time
            logger.info(f"ETL pipeline completed successfully in {elapsed_time:.2f} seconds")
            logger.info(f"Processed: 1 current weather record, {len(forecast_ids)} forecast records")

            return True

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"ETL pipeline failed after {elapsed_time:.2f} seconds: {str(e)}")
            return False

def main():
    """Run the ETL pipeline."""
    city = os.environ.get("WEATHER_CITY", DEFAULT_CITY)
    forecast_days = int(os.environ.get("FORECAST_DAYS", DEFAULT_FORECAST_DAYS))

    pipeline = ETLPipeline(city=city, forecast_days=forecast_days)
    success = pipeline.run()

    if not success:
        logger.error("ETL process failed")
        sys.exit(1)

    logger.info("ETL process completed successfully")

if __name__ == "__main__":
    main()
