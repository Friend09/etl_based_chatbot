# database/db_utils.py

"""
Database utility functions for the Weather ETL Chatbot application.
Provides helper functions for common database operations.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from database.db_connector import DatabaseConnector
from utils.logger import get_component_logger, log_db_function

# Set up logger
logger = get_component_logger('db', 'utils')

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass

def get_value_from_result(result, key_or_index, default=None):
    """
    Helper function to safely extract values from query results,
    which could be either dictionaries or tuples.

    Args:
        result: The query result row (dict or tuple)
        key_or_index: The dictionary key or tuple index
        default: Default value to return if extraction fails

    Returns:
        The extracted value or default
    """
    if result is None:
        return default

    try:
        if isinstance(result, dict):
            return result.get(key_or_index, default)
        elif isinstance(result, (list, tuple)):
            # If the key_or_index is a string but the result is a tuple,
            # we need to convert it to an integer index
            if isinstance(key_or_index, str) and key_or_index == 'location_id':
                return result[0]  # Assume first column is location_id
            elif isinstance(key_or_index, str) and key_or_index == 'weather_id':
                return result[0]  # Assume first column is weather_id
            elif isinstance(key_or_index, str) and key_or_index == 'forecast_id':
                return result[0]  # Assume first column is forecast_id
            elif isinstance(key_or_index, str) and key_or_index == 'report_id':
                return result[0]  # Assume first column is report_id
            elif isinstance(key_or_index, int):
                return result[key_or_index] if 0 <= key_or_index < len(result) else default
            else:
                return default
    except Exception as e:
        logger.warning(f"Failed to extract {key_or_index} from result: {str(e)}")
        return default

@log_db_function
def get_or_create_location(
    city_name: str,
    country: str,
    latitude: float = None,
    longitude: float = None,
    timezone: str = None,
    population: int = None
) -> int:
    """
    Get a location ID from the database by name and country, or create it if it doesn't exist.

    Args:
        city_name (str): Name of the city
        country (str): Country code (e.g., 'US')
        latitude (float, optional): Latitude coordinate
        longitude (float, optional): Longitude coordinate
        timezone (str, optional): Timezone information
        population (int, optional): Population count

    Returns:
        int: The location ID
    """
    db = DatabaseConnector()

    # First try to get the existing location
    try:
        query = """
            SELECT location_id FROM locations
            WHERE city_name = %s AND country = %s
        """
        result = db.execute_query(query, (city_name, country))

        if result:
            # Extract location_id safely
            location_id = get_value_from_result(result[0], 'location_id')
            if location_id is not None:
                logger.debug(f"Found existing location ID {location_id} for {city_name}, {country}")
                return location_id

        # If not found or location_id was None, create a new location
        logger.info(f"Creating new location for {city_name}, {country}")
        insert_query = """
            INSERT INTO locations (city_name, country, latitude, longitude, timezone, population)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING location_id
        """

        result = db.execute_query(
            insert_query,
            (city_name, country, latitude, longitude, timezone, population)
        )

        if not result:
            raise DatabaseError(f"Failed to create location for {city_name}, {country}")

        # Extract location_id safely
        location_id = get_value_from_result(result[0], 'location_id')
        if location_id is None:
            # If still None, try to access as first element of tuple
            location_id = get_value_from_result(result[0], 0)

        if location_id is None:
            raise DatabaseError("Could not extract location_id from database result")

        logger.info(f"Created new location with ID {location_id}")
        return location_id

    except Exception as e:
        logger.error(f"Error getting or creating location: {str(e)}")
        raise

@log_db_function
def save_current_weather(weather_data: Dict[str, Any]) -> int:
    """
    Save current weather data to the database.

    Args:
        weather_data (dict): Weather data from API

    Returns:
        int: The weather_id of the inserted record
    """
    db = DatabaseConnector()

    try:
        # Parse city and country from city string (e.g., "Louisville,KY,US")
        city_parts = weather_data.get('name', '').split(',')
        city_name = city_parts[0]
        country = city_parts[-1] if len(city_parts) > 1 else 'US'

        # Get or create location
        location_id = get_or_create_location(
            city_name,
            country,
            latitude=weather_data.get('coord', {}).get('lat'),
            longitude=weather_data.get('coord', {}).get('lon'),
            timezone=str(weather_data.get('timezone'))
        )

        # Extract weather data
        main_data = weather_data.get('main', {})
        weather_info = weather_data.get('weather', [{}])[0]
        wind_data = weather_data.get('wind', {})

        # Format timestamp
        timestamp = datetime.fromtimestamp(weather_data.get('dt', datetime.now().timestamp()))

        # Insert into weather_current table
        query = """
            INSERT INTO weather_current (
                location_id, timestamp, temperature, feels_like, humidity,
                pressure, wind_speed, wind_direction, weather_condition,
                weather_description, visibility, clouds_percentage, raw_data
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING weather_id
        """

        params = (
            location_id,                                  # location_id
            timestamp,                                    # timestamp
            main_data.get('temp'),                        # temperature
            main_data.get('feels_like'),                  # feels_like
            main_data.get('humidity'),                    # humidity
            main_data.get('pressure'),                    # pressure
            wind_data.get('speed'),                       # wind_speed
            wind_data.get('deg'),                         # wind_direction
            weather_info.get('main'),                     # weather_condition
            weather_info.get('description'),              # weather_description
            weather_data.get('visibility'),               # visibility
            weather_data.get('clouds', {}).get('all'),    # clouds_percentage
            json.dumps(weather_data)                      # raw_data as JSON
        )

        result = db.execute_query(query, params)

        # Extract weather_id safely
        weather_id = get_value_from_result(result[0], 'weather_id')
        if weather_id is None:
            # If still None, try to access as first element of tuple
            weather_id = get_value_from_result(result[0], 0)

        if weather_id is None:
            raise DatabaseError("Could not extract weather_id from database result")

        logger.info(f"Saved current weather with ID {weather_id} for location {location_id}")
        return weather_id

    except Exception as e:
        logger.error(f"Error saving current weather data: {str(e)}")
        raise

@log_db_function
def save_forecast_data(forecast_data: Dict[str, Any]) -> List[int]:
    """
    Save forecast data to the database.

    Args:
        forecast_data (dict): Forecast data from API

    Returns:
        list: List of created forecast IDs
    """
    db = DatabaseConnector()
    forecast_ids = []

    try:
        # Debug logging to help diagnose the structure
        logger.debug(f"Forecast data keys: {list(forecast_data.keys())}")

        # Get city information - this section needs fixing
        city_name = None
        country = 'US'  # Default country code

        # Handle different API response formats
        if 'city' in forecast_data:
            if isinstance(forecast_data['city'], dict):
                city_name = forecast_data['city'].get('name', '')
                country = forecast_data['city'].get('country', 'US')
            else:
                city_name = str(forecast_data['city'])

        # If city not found in standard location, try alternative fields
        if not city_name:
            # Try to get city from top level
            city_name = forecast_data.get('name', '')

        # If still no city name, use a default
        if not city_name:
            city_name = 'Louisville'  # Default city
            logger.warning(f"No city name found in forecast data, using default: {city_name}")

        # Parse city string if it contains country code
        if ',' in city_name:
            city_parts = city_name.split(',')
            city_name = city_parts[0].strip()
            if len(city_parts) > 1 and len(city_parts[-1].strip()) == 2:
                country = city_parts[-1].strip()

        logger.info(f"Processing forecast data for {city_name}, {country}")

        # Get coordinates from the forecast data
        lat = None
        lon = None

        if 'lat' in forecast_data and isinstance(forecast_data['lat'], (int, float)):
            lat = forecast_data['lat']
        elif 'coord' in forecast_data and isinstance(forecast_data['coord'], dict):
            lat = forecast_data['coord'].get('lat')
        elif 'city' in forecast_data and isinstance(forecast_data['city'], dict) and 'coord' in forecast_data['city']:
            lat = forecast_data['city']['coord'].get('lat')

        if 'lon' in forecast_data and isinstance(forecast_data['lon'], (int, float)):
            lon = forecast_data['lon']
        elif 'coord' in forecast_data and isinstance(forecast_data['coord'], dict):
            lon = forecast_data['coord'].get('lon')
        elif 'city' in forecast_data and isinstance(forecast_data['city'], dict) and 'coord' in forecast_data['city']:
            lon = forecast_data['city']['coord'].get('lon')

        # Get timezone information
        timezone = None
        if 'timezone' in forecast_data:
            timezone = forecast_data['timezone']
        elif 'timezone_offset' in forecast_data:
            timezone = str(forecast_data['timezone_offset'])
        elif 'city' in forecast_data and isinstance(forecast_data['city'], dict) and 'timezone' in forecast_data['city']:
            timezone = forecast_data['city']['timezone']

        # Get or create location
        location_id = get_or_create_location(
            city_name,
            country,
            latitude=lat,
            longitude=lon,
            timezone=str(timezone) if timezone else None
        )

        # Get prediction timestamp
        prediction_time = datetime.now()

        # Extract and save daily forecasts
        daily_forecasts = []

        # Try to get forecasts from different possible fields
        if 'daily' in forecast_data and isinstance(forecast_data['daily'], list):
            daily_forecasts = forecast_data['daily']
        elif 'list' in forecast_data and isinstance(forecast_data['list'], list):
            daily_forecasts = forecast_data['list']

        if not daily_forecasts:
            logger.warning("No forecast data found in the response")
            return []

        logger.info(f"Found {len(daily_forecasts)} forecast entries to process")

        # Process each forecast item
        for forecast in daily_forecasts:
            try:
                # Handle different API response formats
                if not isinstance(forecast, dict):
                    logger.warning(f"Skipping non-dict forecast item: {type(forecast)}")
                    continue

                if 'dt' not in forecast:
                    logger.warning("Skipping forecast item without timestamp")
                    continue

                forecast_time = datetime.fromtimestamp(forecast['dt'])

                # Extract temperature data, handling different formats
                temp = None
                feels_like = None

                if 'temp' in forecast:
                    if isinstance(forecast['temp'], dict):
                        # OneCall API format
                        temp = forecast['temp'].get('day')
                        # Check for nested feels_like
                        if 'feels_like' in forecast and isinstance(forecast['feels_like'], dict):
                            feels_like = forecast['feels_like'].get('day')
                    elif isinstance(forecast['temp'], (int, float)):
                        # Simple format
                        temp = forecast['temp']
                elif 'main' in forecast and isinstance(forecast['main'], dict):
                    # 5-day/3-hour API format
                    temp = forecast['main'].get('temp')
                    feels_like = forecast['main'].get('feels_like')

                # Use safer extractions for the rest of the data
                weather_condition = None
                weather_description = None

                if 'weather' in forecast and forecast['weather'] and isinstance(forecast['weather'], list):
                    if forecast['weather'] and isinstance(forecast['weather'][0], dict):
                        weather_condition = forecast['weather'][0].get('main')
                        weather_description = forecast['weather'][0].get('description')

                # Get humidity, with fallbacks
                humidity = None
                if 'humidity' in forecast:
                    humidity = forecast['humidity']
                elif 'main' in forecast and isinstance(forecast['main'], dict):
                    humidity = forecast['main'].get('humidity')

                # Get pressure, with fallbacks
                pressure = None
                if 'pressure' in forecast:
                    pressure = forecast['pressure']
                elif 'main' in forecast and isinstance(forecast['main'], dict):
                    pressure = forecast['main'].get('pressure')

                # Get wind speed, with fallbacks
                wind_speed = None
                if 'wind_speed' in forecast:
                    wind_speed = forecast['wind_speed']
                elif 'wind' in forecast and isinstance(forecast['wind'], dict):
                    wind_speed = forecast['wind'].get('speed')

                # Get wind direction, with fallbacks
                wind_direction = None
                if 'wind_deg' in forecast:
                    wind_direction = forecast['wind_deg']
                elif 'wind' in forecast and isinstance(forecast['wind'], dict):
                    wind_direction = forecast['wind'].get('deg')

                # Get precipitation probability
                precipitation = 0
                if 'pop' in forecast and isinstance(forecast['pop'], (int, float)):
                    precipitation = forecast['pop'] * 100  # Convert to percentage

                # Get clouds percentage
                clouds = None
                if 'clouds' in forecast:
                    if isinstance(forecast['clouds'], dict):
                        clouds = forecast['clouds'].get('all')
                    elif isinstance(forecast['clouds'], (int, float)):
                        clouds = forecast['clouds']

                # Insert into weather_forecast table
                query = """
                    INSERT INTO weather_forecast (
                        location_id, forecast_time, prediction_time, temperature,
                        feels_like, humidity, pressure, wind_speed, wind_direction,
                        weather_condition, weather_description, precipitation_probability,
                        clouds_percentage
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING forecast_id
                """

                params = (
                    location_id,          # location_id
                    forecast_time,        # forecast_time
                    prediction_time,      # prediction_time
                    temp,                 # temperature
                    feels_like,           # feels_like
                    humidity,             # humidity
                    pressure,             # pressure
                    wind_speed,           # wind_speed
                    wind_direction,       # wind_direction
                    weather_condition,    # weather_condition
                    weather_description,  # weather_description
                    precipitation,        # precipitation_probability
                    clouds                # clouds_percentage
                )

                result = db.execute_query(query, params)

                # Extract forecast_id safely
                forecast_id = get_value_from_result(result[0], 'forecast_id')
                if forecast_id is None:
                    forecast_id = get_value_from_result(result[0], 0)

                if forecast_id is not None:
                    forecast_ids.append(forecast_id)

            except Exception as e:
                logger.error(f"Error processing forecast item: {str(e)}")
                # Continue with other forecast items

        logger.info(f"Successfully saved {len(forecast_ids)} forecast items for location {location_id}")
        return forecast_ids

    except Exception as e:
        logger.error(f"Error saving forecast data: {str(e)}")
        raise

@log_db_function
def generate_daily_weather_report(location_id: int, date: datetime.date = None) -> int:
    """
    Generate a daily weather report for a specific location and date.

    Args:
        location_id (int): Location ID
        date (datetime.date, optional): Date for the report. Defaults to today.

    Returns:
        int: Report ID
    """
    db = DatabaseConnector()

    if date is None:
        date = datetime.now().date()

    try:
        # Query to aggregate weather data for the day
        query = """
            WITH daily_data AS (
                SELECT
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp,
                    SUM(precipitation) as total_precip,
                    AVG(humidity) as avg_humidity,
                    STRING_AGG(DISTINCT weather_condition, ', ') as conditions
                FROM weather_current
                WHERE location_id = %s
                AND DATE(timestamp) = %s
            )
            INSERT INTO weather_report (
                location_id, report_date, avg_temperature, min_temperature,
                max_temperature, precipitation_total, avg_humidity, summary
            )
            SELECT
                %s,
                %s,
                avg_temp,
                min_temp,
                max_temp,
                total_precip,
                avg_humidity,
                'Weather summary for ' || TO_CHAR(%s, 'Month DD, YYYY') || ': ' || conditions
            FROM daily_data
            RETURNING report_id
        """

        params = (
            location_id,
            date,
            location_id,
            date,
            date
        )

        result = db.execute_query(query, params)

        if result:
            # Extract report_id safely
            report_id = get_value_from_result(result[0], 'report_id')
            if report_id is None:
                # If still None, try to access as first element of tuple
                report_id = get_value_from_result(result[0], 0)

            if report_id is None:
                raise DatabaseError("Could not extract report_id from database result")

            logger.info(f"Generated weather report {report_id} for location {location_id} on {date}")
            return report_id
        else:
            logger.warning(f"No data available to generate report for location {location_id} on {date}")
            return None

    except Exception as e:
        logger.error(f"Error generating weather report: {str(e)}")
        raise

@log_db_function
def get_latest_weather(location_id: int = None, city_name: str = None, country: str = None) -> Dict:
    """
    Get the latest weather data for a location.

    Args:
        location_id (int, optional): Location ID
        city_name (str, optional): City name (alternative to location_id)
        country (str, optional): Country code (used with city_name)

    Returns:
        dict: Latest weather data or None if not found
    """
    db = DatabaseConnector()

    try:
        if not location_id and (city_name and country):
            # Get location_id from city_name and country
            query = "SELECT location_id FROM locations WHERE city_name = %s AND country = %s"
            result = db.execute_query(query, (city_name, country))

            if not result:
                logger.warning(f"No location found for {city_name}, {country}")
                return None

            # Extract location_id safely
            location_id = get_value_from_result(result[0], 'location_id')
            if location_id is None:
                # If still None, try to access as first element of tuple
                location_id = get_value_from_result(result[0], 0)

            if location_id is None:
                logger.warning(f"Could not extract location_id for {city_name}, {country}")
                return None

        if not location_id:
            logger.error("Either location_id or both city_name and country must be provided")
            return None

        # Query latest weather data
        query = """
            SELECT w.*, l.city_name, l.country, l.latitude, l.longitude, l.timezone
            FROM weather_current w
            JOIN locations l ON w.location_id = l.location_id
            WHERE w.location_id = %s
            ORDER BY w.timestamp DESC
            LIMIT 1
        """

        result = db.execute_query(query, (location_id,))

        if result:
            logger.info(f"Successfully retrieved latest weather for location {location_id}")
            return result[0]
        else:
            logger.warning(f"No weather data found for location {location_id}")
            return None

    except Exception as e:
        logger.error(f"Error getting latest weather: {str(e)}")
        raise
