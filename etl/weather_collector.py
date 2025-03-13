"""
Module for collecting weather data from OpenWeatherMap API.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_component_logger, log_etl_function, log_structured
from utils.location_validator import validate_city_format
from config.settings import OPENWEATHERMAP_API_KEY, CONFIG_DIR
from database.db_utils import save_current_weather, save_forecast_data

# Get component-specific logger
logger = get_component_logger('etl', 'weather_collector')

# API configuration
API_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_API_BASE_URL = "http://api.openweathermap.org/geo/1.0"  # Geocoding API
ONECALL_API_URL = "https://api.openweathermap.org/data/3.0/onecall"  # Updated OneCall API
FORECAST_DAILY_URL = "https://api.openweathermap.org/data/2.5/forecast/daily"  # 16-day forecast API
FORECAST_5DAY_URL = "https://api.openweathermap.org/data/2.5/forecast"  # 5-day/3-hour forecast API
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
DEFAULT_CITY = "Louisville,KY,US"

class WeatherCollector:
    """
    Handles collection of weather data from the OpenWeatherMap API
    for Louisville, KY.
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    API_KEY = OPENWEATHERMAP_API_KEY

    def __init__(self, lat=38.2527, lon=-85.7585, city="Louisville", api_key=None):
        """
        Initialize the WeatherCollector with API configuration.

        Args:
            lat (float): Latitude for the location (default: Louisville, KY)
            lon (float): Longitude for the location (default: Louisville, KY)
            city (str): City name (default: Louisville)
            api_key (str, optional): OpenWeatherMap API key. If not provided,
                                    it will use the key from environment variable.
        """
        self.api_key = api_key or self.API_KEY

        if not self.api_key:
            self._handle_missing_api_key()

        self.lat = lat
        self.lon = lon
        self.city = city
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.current_weather_url = f"{self.base_url}/weather"
        self.forecast_url = f"{self.base_url}/forecast"

    def _handle_missing_api_key(self):
        """Handle missing API key with helpful error message."""
        example_file_path = os.path.join(CONFIG_DIR, '.env.example')
        env_file_path = os.path.join(project_root, '.env')

        error_message = (
            "OpenWeatherMap API key not found. Please set OPENWEATHERMAP_API_KEY environment variable.\n"
            "You can obtain an API key from: https://openweathermap.org/api\n\n"
            "To fix this issue:\n"
            "1. Create or edit the .env file in the project root\n"
            f"2. Add the line: OPENWEATHERMAP_API_KEY=your_api_key_here\n"
            "3. Restart the application\n"
        )

        # Create .env.example file if it doesn't exist
        if not os.path.exists(example_file_path):
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(example_file_path, 'w') as f:
                f.write("# OpenWeatherMap API key\n")
                f.write("OPENWEATHERMAP_API_KEY=your_api_key_here\n\n")
                f.write("# Database Configuration\n")
                f.write("DB_HOST=localhost\n")
                f.write("DB_PORT=5432\n")
                f.write("DB_NAME=weather_db\n")
                f.write("DB_USER=postgres\n")
                f.write("DB_PASSWORD=your_password\n")

        logger.error("OpenWeatherMap API key not found. Please set OPENWEATHERMAP_API_KEY environment variable.")
        print(error_message, file=sys.stderr)

        # Don't exit here, let the caller decide what to do

    def fetch_current_weather(self):
        """
        Fetch current weather data from OpenWeatherMap API.

        Returns:
            dict: Raw current weather data from API
        """
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        response = requests.get(self.current_weather_url, params=params)
        response.raise_for_status()
        return response.json()

    def fetch_forecast(self):
        """
        Fetch forecast data from OpenWeatherMap API.

        Returns:
            dict: Raw forecast data from API
        """
        params = {
            'lat': self.lat,
            'lon': self.lon,
            'appid': self.api_key,
            'units': 'metric'  # Celsius
        }
        response = requests.get(self.forecast_url, params=params)
        response.raise_for_status()
        return response.json()

    def process_current_weather(self, data):
        """
        Process the current weather data into a structured format.

        Args:
            data (dict): Raw current weather data from API

        Returns:
            dict: Processed current weather data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'city': self.city,
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'raw_data': data
        }

    def process_forecast(self, data):
        """
        Process the forecast data into a structured format.

        Args:
            data (dict): Raw forecast data from API

        Returns:
            list: List of processed forecast entries
        """
        processed_data = []
        for forecast in data['list']:
            processed_entry = {
                'forecast_timestamp': forecast['dt_txt'],
                'city': self.city,
                'temperature': forecast['main']['temp'],
                'feels_like': forecast['main']['feels_like'],
                'humidity': forecast['main']['humidity'],
                'pressure': forecast['main']['pressure'],
                'wind_speed': forecast['wind']['speed'],
                'weather_main': forecast['weather'][0]['main'],
                'weather_description': forecast['weather'][0]['description'],
                'raw_data': forecast
            }
            processed_data.append(processed_entry)
        return processed_data

    def save_current_weather(self, processed_data):
        """
        Save the processed current weather data to storage.

        Args:
            processed_data (dict): Processed current weather data

        Returns:
            bool: Success status
        """
        # Placeholder for actual database save implementation
        # In a real implementation, this would save to a database
        return True

    def save_forecast(self, processed_data):
        """
        Save the processed forecast data to storage.

        Args:
            processed_data (list): List of processed forecast entries

        Returns:
            bool: Success status
        """
        # Placeholder for actual database save implementation
        # In a real implementation, this would save to a database
        return True

    def collect_and_store(self):
        """
        Collect, process, and store both current weather and forecast data.

        Returns:
            tuple: (current_weather_success, forecast_success)
        """
        # Fetch data
        current_data = self.fetch_current_weather()
        forecast_data = self.fetch_forecast()

        # Process data
        processed_current = self.process_current_weather(current_data)
        processed_forecast = self.process_forecast(forecast_data)

        # Save data
        current_success = self.save_current_weather(processed_current)
        forecast_success = self.save_forecast(processed_forecast)

        return current_success, forecast_success

# Helper functions for backwards compatibility
class APIError(Exception):
    """Exception raised for API-related errors."""
    pass

@log_etl_function
def get_current_weather(city=DEFAULT_CITY, api_key=None):
    """
    Fetch current weather data for a specific city.

    Args:
        city (str): City name (and optional country code)
        api_key (str): OpenWeatherMap API key (uses env var if None)

    Returns:
        dict: Weather data

    Raises:
        APIError: If the API request fails
    """
    api_key = api_key or API_KEY

    if not api_key:
        logger.error("No API key provided for OpenWeatherMap")
        raise APIError("API key is required")

    endpoint = f"{API_BASE_URL}/weather"

    logger.info(f"Fetching current weather data for {city}")

    try:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'  # Use metric units (Celsius)
        }

        # Log the API call (without the API key for security)
        safe_params = params.copy()
        safe_params['appid'] = '***REDACTED***'
        logger.debug(f"Making API request to {endpoint} with params: {safe_params}")

        response = requests.get(endpoint, params=params, timeout=10)

        # Check response status
        response.raise_for_status()

        data = response.json()

        # Log successful response
        log_structured(
            logger,
            "info",
            "api_success",
            endpoint="weather",
            city=city,
            status_code=response.status_code
        )

        logger.info(f"Successfully retrieved weather data for {city}")
        return data

    except requests.RequestException as e:
        # Log detailed error information
        log_structured(
            logger,
            "error",
            "api_error",
            endpoint="weather",
            error_message=str(e),
            status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        )

        logger.error(f"Failed to fetch weather data: {str(e)}")
        raise APIError(f"Failed to fetch weather data: {str(e)}") from e

@log_etl_function
def get_forecast(city=DEFAULT_CITY, api_key=None, days=5):
    """
    Fetch weather forecast data for a specific city.

    This function tries multiple API endpoints in the following order:
    1. OneCall API 3.0 (requires subscription)
    2. OneCall API 2.5 (fallback)
    3. 16-day Daily Forecast API (second fallback)

    Args:
        city (str): City name (and optional country code)
        api_key (str): OpenWeatherMap API key (uses env var if None)
        days (int): Number of days for forecast (max 16)

    Returns:
        dict: Forecast data

    Raises:
        APIError: If all API methods fail
    """
    api_key = api_key or API_KEY

    if not api_key:
        logger.error("No API key provided for OpenWeatherMap")
        raise APIError("API key is required")

    # Get coordinates first using the geocoding API
    logger.info(f"Fetching {days}-day forecast for {city}")

    try:
        # Step 1: Get geo coordinates from city name
        geo_endpoint = f"{GEO_API_BASE_URL}/direct"
        geo_params = {
            'q': city,
            'limit': 1,
            'appid': api_key
        }

        logger.debug(f"Getting geo coordinates for {city}")
        logger.debug(f"Geocoding API URL: {geo_endpoint}")

        geo_response = requests.get(geo_endpoint, params=geo_params, timeout=10)
        geo_response.raise_for_status()

        locations = geo_response.json()
        if not locations:
            logger.warning(f"No location found for '{city}'. Try a different city name or format.")
            raise APIError(f"No location found for {city}")

        lat = locations[0]['lat']
        lon = locations[0]['lon']
        logger.debug(f"Found coordinates: lat={lat}, lon={lon}")

        # Try all forecast APIs, starting with the most comprehensive
        return _try_all_forecast_apis(lat, lon, api_key, days)

    except requests.RequestException as e:
        log_structured(
            logger,
            "error",
            "api_error",
            endpoint="geocoding",
            method="GET",
            error_code=getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500,
            error_message=f"Geocoding error: {str(e)}"
        )

        logger.error(f"Failed to get coordinates: {str(e)}")
        raise APIError(f"Failed to get coordinates for {city}: {str(e)}") from e

@log_etl_function
def _try_all_forecast_apis(lat, lon, api_key, days=5):
    """
    Try different forecast APIs in sequence until one succeeds.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key
        days (int): Number of days for forecast

    Returns:
        dict: Forecast data

    Raises:
        APIError: If all API methods fail
    """
    # Error collection for better error reporting
    errors = []

    # Try 5-day/3-hour forecast API first as it's usually available with free accounts
    try:
        logger.info("Attempting to use 5-day/3-hour Forecast API (most widely available)")
        forecast_data = _get_5day_forecast(lat, lon, api_key)
        forecast_data['api_source'] = "forecast_5day"
        return forecast_data
    except Exception as e:
        errors.append(f"5-day/3-hour Forecast API failed: {str(e)}")
        logger.warning(f"5-day/3-hour Forecast API failed: {str(e)}")

    # Try OneCall API 3.0 if explicitly enabled
    if os.environ.get('USE_ONECALL_V3', 'false').lower() == 'true':
        try:
            logger.info("Attempting to use OneCall API 3.0")
            forecast_data = _get_onecall_v3_forecast(lat, lon, api_key, days)
            forecast_data['api_source'] = "onecall_v3"
            return forecast_data
        except Exception as e:
            errors.append(f"OneCall API 3.0 failed: {str(e)}")
            logger.warning(f"OneCall API 3.0 failed: {str(e)}")

    # Try OneCall API 2.5 if explicitly enabled
    if os.environ.get('USE_ONECALL_V25', 'false').lower() == 'true':
        try:
            logger.info("Attempting to use OneCall API 2.5")
            forecast_data = _get_onecall_v25_forecast(lat, lon, api_key, days)
            forecast_data['api_source'] = "onecall_v25"
            return forecast_data
        except Exception as e:
            errors.append(f"OneCall API 2.5 failed: {str(e)}")
            logger.warning(f"OneCall API 2.5 failed: {str(e)}")

    # Try 16-day forecast API if explicitly enabled
    if os.environ.get('USE_DAILY_FORECAST', 'false').lower() == 'true':
        try:
            logger.info("Attempting to use 16-day Daily Forecast API")
            forecast_data = _get_daily_forecast(lat, lon, api_key, days)
            forecast_data['api_source'] = "daily_forecast"
            return forecast_data
        except Exception as e:
            errors.append(f"16-day Daily Forecast API failed: {str(e)}")
            logger.error(f"16-day Daily Forecast API also failed: {str(e)}")

    # If we get here, all methods failed
    error_message = "; ".join(errors)
    raise APIError(f"All forecast API methods failed: {error_message}")

@log_etl_function
def _get_onecall_v3_forecast(lat, lon, api_key, days=5):
    """
    Get forecast using OneCall API 3.0.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key
        days (int): Number of days for forecast

    Returns:
        dict: Forecast data
    """
    forecast_params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,alerts',
        'appid': api_key,
        'units': 'metric'
    }

    logger.debug(f"Making API request to {ONECALL_API_URL}")

    response = requests.get(ONECALL_API_URL, params=forecast_params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Limit daily forecast to requested number of days (max 8)
    if 'daily' in data and days < 8:
        data['daily'] = data['daily'][:min(days, 8)]

    logger.info(f"Successfully retrieved {len(data.get('daily', []))} days forecast using OneCall API 3.0")
    return data

@log_etl_function
def _get_onecall_v25_forecast(lat, lon, api_key, days=5):
    """
    Get forecast using OneCall API 2.5.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key
        days (int): Number of days for forecast

    Returns:
        dict: Forecast data
    """
    endpoint = f"{API_BASE_URL}/onecall"

    params = {
        'lat': lat,
        'lon': lon,
        'exclude': 'minutely,alerts',
        'appid': api_key,
        'units': 'metric'
    }

    logger.debug(f"Making API request to {endpoint}")

    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Limit daily forecast to requested number of days
    if 'daily' in data:
        data['daily'] = data['daily'][:min(days, len(data['daily']))]

    logger.info(f"Successfully retrieved {len(data.get('daily', []))} days forecast using OneCall API 2.5")
    return data

@log_etl_function
def _get_daily_forecast(lat, lon, api_key, days=5):
    """
    Get forecast using the 16-day Daily Forecast API.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key
        days (int): Number of days for forecast (max 16)

    Returns:
        dict: Forecast data
    """
    days = min(16, max(1, days))  # Ensure days is between 1 and 16

    params = {
        'lat': lat,
        'lon': lon,
        'cnt': days,  # Number of days
        'appid': api_key,
        'units': 'metric'
    }

    logger.debug(f"Making API request to {FORECAST_DAILY_URL}")

    response = requests.get(FORECAST_DAILY_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Map the response structure to match OneCall as closely as possible for consistency
    mapped_data = {
        'lat': data.get('city', {}).get('coord', {}).get('lat'),
        'lon': data.get('city', {}).get('coord', {}).get('lon'),
        'timezone': data.get('city', {}).get('timezone'),
        'timezone_offset': data.get('city', {}).get('timezone'),
        'daily': data.get('list', [])
    }

    logger.info(f"Successfully retrieved {len(mapped_data.get('daily', []))} days forecast using Daily Forecast API")
    return mapped_data

@log_etl_function
def _get_5day_forecast(lat, lon, api_key):
    """
    Get forecast using the 5-day/3-hour Forecast API (free tier compatible).

    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key

    Returns:
        dict: Forecast data
    """
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'metric'
    }

    logger.debug(f"Making API request to {FORECAST_5DAY_URL}")

    response = requests.get(FORECAST_5DAY_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Map the response structure to be consistent with other formats
    # This API returns forecast in 3-hour steps, so we need to group by day
    daily_forecasts = []
    current_date = None
    daily_data = None

    for item in data.get('list', []):
        # Convert timestamp to date
        dt = datetime.fromtimestamp(item['dt'])
        date_str = dt.strftime('%Y-%m-%d')

        # Group forecasts by day
        if date_str != current_date:
            if daily_data:
                daily_forecasts.append(daily_data)

            # Start a new day's data
            current_date = date_str
            daily_data = {
                'dt': item['dt'],
                'sunrise': None,  # Not provided in this API
                'sunset': None,   # Not provided in this API
                'temp': {
                    'day': item['main']['temp'],
                    'min': item['main']['temp_min'],
                    'max': item['main']['temp_max'],
                },
                'feels_like': {
                    'day': item['main']['feels_like']
                },
                'pressure': item['main']['pressure'],
                'humidity': item['main']['humidity'],
                'weather': item['weather'],
                'wind_speed': item['wind']['speed'],
                'wind_deg': item['wind']['deg'],
                'clouds': item['clouds']['all'],
                'pop': item.get('pop', 0),  # Probability of precipitation
                'rain': item.get('rain', {'3h': 0}).get('3h', 0),
                'date': date_str
            }
        else:
            # Update min/max for the current day
            daily_data['temp']['min'] = min(daily_data['temp']['min'], item['main']['temp_min'])
            daily_data['temp']['max'] = max(daily_data['temp']['max'], item['main']['temp_max'])

            # Add precipitation if available
            if 'rain' in item and '3h' in item['rain']:
                daily_data['rain'] += item['rain']['3h']

    # Add the last day
    if daily_data:
        daily_forecasts.append(daily_data)

    # Create a consistent structure
    mapped_data = {
        'lat': data['city']['coord']['lat'],
        'lon': data['city']['coord']['lon'],
        'timezone': data['city']['timezone'],
        'timezone_offset': data['city']['timezone'],
        'city': data['city']['name'],
        'country': data['city']['country'],
        'daily': daily_forecasts,
        'api_type': '5day_forecast'
    }

    logger.info(f"Successfully retrieved {len(daily_forecasts)} days forecast using 5-day/3-hour Forecast API")
    return mapped_data

@log_etl_function
def save_weather_data(data, output_dir="data/weather", filename=None):
    """
    Save weather data to a JSON file.

    Args:
        data (dict): Weather data to save
        output_dir (str): Directory to save data to
        filename (str): Optional custom filename

    Returns:
        str: Path to saved file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename based on current time if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_{timestamp}.json"

    file_path = output_path / filename

    try:
        logger.info(f"Saving weather data to {file_path}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Weather data successfully saved to {file_path}")
        return str(file_path)

    except Exception as e:
        logger.error(f"Failed to save weather data: {str(e)}")
        raise

def main():
    """
    Main function to collect and save weather data.
    """
    logger.info("Starting weather data collection")

    try:
        # Check if API key is available
        if not API_KEY:
            logger.error("OpenWeatherMap API key not found. Please set OPENWEATHERMAP_API_KEY environment variable.")
            sys.exit(1)

        # Get city from environment and validate format
        city = os.environ.get("WEATHER_CITY", DEFAULT_CITY)
        city = validate_city_format(city)
        logger.info(f"Using city: {city}")

        # Get current weather
        current_weather = get_current_weather(city)

        # Save current weather data to file
        save_weather_data(current_weather, filename=f"current_{datetime.now().strftime('%Y%m%d')}.json")

        # Save current weather to database
        try:
            weather_id = save_current_weather(current_weather)
            logger.info(f"Current weather data saved to database with ID: {weather_id}")
        except Exception as e:
            logger.error(f"Failed to save current weather to database: {str(e)}")

        try:
            # Get forecast data (up to 8 days with OneCall API 3.0)
            forecast_data = get_forecast(city, days=8)

            # Save forecast data to file
            save_weather_data(forecast_data, filename=f"forecast_{datetime.now().strftime('%Y%m%d')}.json")

            # Save forecast data to database
            try:
                forecast_ids = save_forecast_data(forecast_data)
                logger.info(f"Forecast data saved to database: {len(forecast_ids)} entries")
            except Exception as e:
                logger.error(f"Failed to save forecast data to database: {str(e)}")

        except APIError as e:
            logger.warning(f"Could not retrieve forecast data: {str(e)}")
            logger.warning("Continuing with just current weather data")

        logger.info("Weather data collection completed successfully")

    except Exception as e:
        logger.error(f"Weather data collection failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
