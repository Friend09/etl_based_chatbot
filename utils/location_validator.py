"""
Utility for validating and formatting location inputs for weather API calls.
"""

import re
from utils.logger import setup_logger

logger = setup_logger("location_validator")

def validate_city_format(city_input):
    """
    Validates and formats city input for OpenWeatherMap API.

    Recommended formats:
    - "City"
    - "City,CountryCode" (2-letter ISO code)
    - "City,State,CountryCode" (for US cities)

    Args:
        city_input (str): City input to validate

    Returns:
        str: Formatted city string or original if no changes needed
    """
    if not city_input:
        logger.warning("Empty city input provided")
        return "London"  # Default fallback

    # Trim whitespace and fix common issues
    city = city_input.strip()

    # Check if format seems correct (City,State,Country or City,Country)
    parts = [part.strip() for part in city.split(',')]

    if len(parts) == 1:
        logger.info(f"Using city name only: {parts[0]}")
        return parts[0]

    if len(parts) == 2:
        # Ensure country code is uppercase for 2-letter codes
        if len(parts[1]) == 2:
            parts[1] = parts[1].upper()
        logger.info(f"Using City,Country format: {parts[0]},{parts[1]}")
        return f"{parts[0]},{parts[1]}"

    if len(parts) == 3:
        # For US cities: City,State,US
        if parts[2].upper() == "US" and len(parts[1]) == 2:
            parts[1] = parts[1].upper()
            parts[2] = parts[2].upper()
        logger.info(f"Using City,State,Country format: {parts[0]},{parts[1]},{parts[2]}")
        return f"{parts[0]},{parts[1]},{parts[2]}"

    logger.warning(f"Unusual city format: {city_input}, using as-is")
    return city_input

def test_location_format(city_input):
    """
    Test if a location can be properly geocoded by the OpenWeatherMap API.

    Args:
        city_input (str): City input to test

    Returns:
        dict: {'valid': bool, 'formatted': str, 'message': str}
    """
    import os
    import requests

    API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not API_KEY:
        return {
            'valid': False,
            'formatted': city_input,
            'message': "API key not available. Cannot test location."
        }

    # Format the city
    formatted_city = validate_city_format(city_input)

    try:
        # Test geocoding
        geo_endpoint = "http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            'q': formatted_city,
            'limit': 1,
            'appid': API_KEY
        }

        response = requests.get(geo_endpoint, params=geo_params, timeout=10)
        response.raise_for_status()

        locations = response.json()
        if not locations:
            return {
                'valid': False,
                'formatted': formatted_city,
                'message': f"No location found for '{formatted_city}'. Try a different format."
            }

        # Success - found location
        location = locations[0]
        return {
            'valid': True,
            'formatted': formatted_city,
            'message': f"Found: {location.get('name', '')}, {location.get('country', '')}",
            'location': location
        }

    except Exception as e:
        return {
            'valid': False,
            'formatted': formatted_city,
            'message': f"Error testing location: {str(e)}"
        }

if __name__ == "__main__":
    # Test some city formats
    test_cities = [
        "London",
        "New York",
        "Paris,FR",
        "Rome, IT",  # with space
        "Louisville,KY,US",  # format in your logs
        "Louisville, KY, US",  # with spaces
        "Tokyo,Japan",  # with full country name
        "Invalid,XX,YY"  # likely invalid
    ]

    print("\nTesting city formats:")
    print("---------------------")

    for city in test_cities:
        formatted = validate_city_format(city)
        print(f"Original: '{city}' → Formatted: '{formatted}'")

        # Test geocoding
        result = test_location_format(city)
        status = "✅" if result['valid'] else "❌"
        print(f"  {status} {result['message']}\n")
