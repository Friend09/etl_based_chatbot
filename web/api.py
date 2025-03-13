"""
API endpoints for the weather data.
"""

from flask import Blueprint, jsonify, request
import requests
import os

from utils.logger import get_component_logger, log_web_function, log_structured
from utils.location_validator import validate_city_format

# Create a logger for this module
logger = get_component_logger('web', 'api')

# Create a blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# API configuration
API_BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_API_BASE_URL = "http://api.openweathermap.org/geo/1.0"
ONECALL_API_URL = "https://api.openweathermap.org/data/3.0/onecall"
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

@api_bp.route('/weather', methods=['GET'])
@log_web_function
def get_weather():
    """Get current weather data for a location."""
    location = request.args.get('location', 'Louisville,KY,US')

    log_structured(
        logger,
        "info",
        "api_request",
        endpoint="/weather",
        method="GET",
        params={"location": location},
        response_time=0.25  # Placeholder value
    )

    try:
        # Implement actual API call to OpenWeatherMap
        params = {
            'q': location,
            'appid': API_KEY,
            'units': 'metric'
        }

        response = requests.get(f"{API_BASE_URL}/weather", params=params)
        response.raise_for_status()

        return jsonify(response.json()), 200

    except requests.exceptions.RequestException as e:
        log_structured(
            logger,
            "error",
            "api_error",
            endpoint="/weather",
            method="GET",
            error_code=getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500,
            error_message=str(e)
        )
        return jsonify({"error": str(e)}), 500

@api_bp.route('/forecast', methods=['GET', 'POST'])
@log_web_function
def get_forecast():
    """Get weather forecast for a location."""
    # Handle both GET and POST methods
    if request.method == 'POST':
        data = request.json
        location = data.get('location', 'Louisville,KY,US')
        days = data.get('days', 5)
    else:  # GET
        location = request.args.get('location', 'Louisville,KY,US')
        days = request.args.get('days', 5, type=int)

    # Validate and format the location
    location = validate_city_format(location)
    logger.info(f"Forecast requested for {location} ({days} days)")

    try:
        # Check if API key is available
        if not API_KEY:
            raise ValueError("OpenWeatherMap API key not configured")

        # First get geo coordinates from city name
        geo_endpoint = f"{GEO_API_BASE_URL}/direct"
        geo_params = {
            'q': location,
            'limit': 1,
            'appid': API_KEY
        }

        logger.debug(f"Geocoding API URL: {geo_endpoint}")
        geo_response = requests.get(geo_endpoint, params=geo_params, timeout=10)
        geo_response.raise_for_status()

        locations = geo_response.json()
        if not locations:
            logger.warning(f"No location found for {location}")
            return jsonify({"error": f"Location '{location}' not found"}), 404

        lat = locations[0]['lat']
        lon = locations[0]['lon']

        # Try OneCall API 3.0 first
        try:
            # Get forecast using OneCall API 3.0
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'exclude': 'minutely,alerts',
                'appid': API_KEY,
                'units': 'metric'
            }

            forecast_response = requests.get(ONECALL_API_URL, params=forecast_params, timeout=10)
            forecast_response.raise_for_status()

            forecast_data = forecast_response.json()
            api_version = "3.0"

        except requests.exceptions.RequestException as e:
            # Fallback to OneCall API 2.5 if 3.0 fails
            logger.warning(f"OneCall API 3.0 failed ({str(e)}), falling back to 2.5")

            fallback_endpoint = f"{API_BASE_URL}/onecall"
            fallback_params = {
                'lat': lat,
                'lon': lon,
                'exclude': 'minutely,alerts',
                'appid': API_KEY,
                'units': 'metric'
            }

            forecast_response = requests.get(fallback_endpoint, params=fallback_params, timeout=10)
            forecast_response.raise_for_status()

            forecast_data = forecast_response.json()
            api_version = "2.5"

        # Limit to requested number of days
        if 'daily' in forecast_data:
            forecast_data['daily'] = forecast_data['daily'][:min(days, len(forecast_data['daily']))]

        # Add API version info to response
        forecast_data['api_version'] = api_version

        log_structured(
            logger,
            "info",
            "api_request",
            endpoint="/forecast",
            method=request.method,
            params={"location": location, "days": days},
            api_version=api_version,
            status_code=200
        )

        return jsonify(forecast_data), 200

    except (requests.exceptions.RequestException, ValueError) as e:
        error_code = 500
        if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
            error_code = e.response.status_code

        log_structured(
            logger,
            "error",
            "api_error",
            endpoint="/forecast",
            method=request.method,
            error_code=error_code,
            error_message=str(e)
        )
        return jsonify({"error": str(e)}), error_code
