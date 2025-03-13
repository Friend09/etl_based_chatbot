"""
Weather data collector module for the Louisville weather ETL pipeline.
Fetches data from OpenWeatherMap API and stores it in the database.
"""

import requests
import json
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from config.settings import (
    OPENWEATHERMAP_API_KEY,
    CITY,
    COUNTRY_CODE,
    LAT,
    LON,
    COLLECTION_INTERVAL
)
from database.db_connector import DatabaseConnector

# Set up logging
logger = logging.getLogger(__name__)

class WeatherCollector:
    """
    Class to collect weather data from OpenWeatherMap API.
    Handles both current weather and forecast data.
    """

    def __init__(self):
        """Initialize the weather collector with API settings."""
        self.api_key = OPENWEATHERMAP_API_KEY
        self.city = CITY
        self.country_code = COUNTRY_CODE
        self.lat = LAT
        self.lon = LON
        self.db = DatabaseConnector()

        # API endpoints
        self.current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"

        # Check if API key is available
        if not self.api_key:
            logger.error("OpenWeatherMap API key not found in environment variables.")
            raise ValueError("API key not found. Please set OPENWEATHERMAP_API_KEY in .env file.")

    def fetch_current_weather(self):
        """
        Fetch current weather data for the configured location.

        Returns:
            dict: JSON response from the API or None if the request failed
        """
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": "metric"  # Use metric units (Celsius, meters/sec)
        }

        try:
            logger.info(f"Fetching current weather data for {self.city}, {self.country_code}")
            response = requests.get(self.current_weather_url, params=params)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            data = response.json()
            logger.debug(f"Successfully retrieved current weather data: {data}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching current weather data: {e}")
            return None

    def fetch_forecast(self):
        """
        Fetch 5-day/3-hour forecast data for the configured location.

        Returns:
            dict: JSON response from the API or None if the request failed
        """
        params = {
            "lat": self.lat,
            "lon": self.lon,
            "appid": self.api_key,
            "units": "metric"  # Use metric units (Celsius, meters/sec)
        }

        try:
            logger.info(f"Fetching weather forecast data for {self.city}, {self.country_code}")
            response = requests.get(self.forecast_url, params=params)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Successfully retrieved forecast data with {len(data.get('list', []))} entries")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching forecast data: {e}")
            return None

    def process_current_weather(self, data):
        """
        Process current weather data and prepare it for database insertion.

        Args:
            data (dict): Raw API response for current weather

        Returns:
            dict: Processed data ready for database insertion
        """
        if not data:
            return None

        try:
            # Extract relevant fields
            processed_data = {
                "timestamp": datetime.now(),
                "city": self.city,
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"]["deg"],
                "weather_main": data["weather"][0]["main"],
                "weather_description": data["weather"][0]["description"],
                "clouds": data["clouds"]["all"],
                "visibility": data.get("visibility"),
                "rain_1h": data.get("rain", {}).get("1h"),
                "snow_1h": data.get("snow", {}).get("1h"),
                "raw_data": json.dumps(data)
            }
            return processed_data

        except KeyError as e:
            logger.error(f"Error processing current weather data, missing key: {e}")
            return None

    def process_forecast(self, data):
        """
        Process forecast data and prepare it for database insertion.

        Args:
            data (dict): Raw API response for forecast

        Returns:
            list: List of processed forecast entries ready for database insertion
        """
        if not data or "list" not in data:
            return []

        processed_entries = []
        collection_time = datetime.now()

        try:
            for entry in data["list"]:
                forecast_time = datetime.fromtimestamp(entry["dt"])

                processed_entry = {
                    "collection_timestamp": collection_time,
                    "forecast_timestamp": forecast_time,
                    "city": self.city,
                    "temperature": entry["main"]["temp"],
                    "feels_like": entry["main"]["feels_like"],
                    "humidity": entry["main"]["humidity"],
                    "pressure": entry["main"]["pressure"],
                    "wind_speed": entry["wind"]["speed"],
                    "wind_direction": entry["wind"]["deg"],
                    "weather_main": entry["weather"][0]["main"],
                    "weather_description": entry["weather"][0]["description"],
                    "clouds": entry["clouds"]["all"],
                    "visibility": entry.get("visibility"),
                    "pop": entry.get("pop"),  # Probability of precipitation
                    "rain_3h": entry.get("rain", {}).get("3h"),
                    "snow_3h": entry.get("snow", {}).get("3h"),
                    "raw_data": json.dumps(entry)
                }

                processed_entries.append(processed_entry)

            return processed_entries

        except KeyError as e:
            logger.error(f"Error processing forecast data, missing key: {e}")
            return []

    def save_current_weather(self, processed_data):
        """
        Save processed current weather data to the database.

        Args:
            processed_data (dict): Processed weather data

        Returns:
            int or None: ID of the inserted record or None if failed
        """
        if not processed_data:
            return None

        try:
            record_id = self.db.insert_json_data("weather_current", processed_data, return_id=True)
            logger.info(f"Saved current weather data with ID: {record_id}")
            return record_id

        except Exception as e:
            logger.error(f"Error saving current weather data to database: {e}")
            return None

    def save_forecast(self, processed_entries):
        """
        Save processed forecast data to the database.

        Args:
            processed_entries (list): List of processed forecast entries

        Returns:
            int: Number of records inserted
        """
        if not processed_entries:
            return 0

        total_saved = 0

        try:
            # Split into chunks to avoid too many parameters in one query
            chunk_size = 50
            chunks = [processed_entries[i:i+chunk_size] for i in range(0, len(processed_entries), chunk_size)]

            for chunk in chunks:
                # Build batch insert query
                keys = list(chunk[0].keys())
                columns = ", ".join(keys)
                placeholders = ", ".join([f"%({key})s" for key in keys])

                query = f"INSERT INTO weather_forecasts ({columns}) VALUES ({placeholders})"

                # Execute batch insert
                rows_affected = self.db.execute_many(query, chunk)
                total_saved += rows_affected

            logger.info(f"Saved {total_saved} forecast entries to database")
            return total_saved

        except Exception as e:
            logger.error(f"Error saving forecast data to database: {e}")
            return 0

    def collect_and_store(self):
        """
        Execute the complete data collection and storage process.
        Fetches both current weather and forecast data in parallel.
        """
        logger.info("Starting weather data collection")

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Fetch data in parallel
            current_weather_future = executor.submit(self.fetch_current_weather)
            forecast_future = executor.submit(self.fetch_forecast)

            # Get results from futures
            current_weather = current_weather_future.result()
            forecast = forecast_future.result()

        # Process and save current weather
        if current_weather:
            processed_current = self.process_current_weather(current_weather)
            self.save_current_weather(processed_current)

        # Process and save forecast
        if forecast:
            processed_forecast = self.process_forecast(forecast)
            self.save_forecast(processed_forecast)

        logger.info("Completed weather data collection")

def run_collector():
    """Run the weather collector once."""
    collector = WeatherCollector()
    collector.collect_and_store()

def continuous_collection():
    """Run the weather collector continuously at the specified interval."""
    logger.info(f"Starting continuous weather data collection every {COLLECTION_INTERVAL} seconds")

    while True:
        try:
            run_collector()
            time.sleep(COLLECTION_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Weather data collection stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in continuous collection: {e}")
            time.sleep(60)  # Wait a minute before retrying if there's an error

def main():
    """Main entry point for the weather collector script."""
    import argparse

    parser = argparse.ArgumentParser(description="Collect weather data from OpenWeatherMap API")
    parser.add_argument("--continuous", action="store_true", help="Run continuously at specified interval")
    args = parser.parse_args()

    if args.continuous:
        continuous_collection()
    else:
        run_collector()

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
