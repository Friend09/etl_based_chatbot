"""
Location validation utilities for ensuring consistent city formats for weather API calls.
"""

import re
from utils.logger import get_component_logger

# Get component-specific logger
logger = get_component_logger('utils', 'location_validator')

def validate_city_format(city_str):
    """
    Validate and normalize city format as "City,State,Country" or "City,Country".

    The function accepts various input formats:
    - "City"
    - "City, State"
    - "City, State, Country"
    - "City,State"
    - "City,State,Country"

    Args:
        city_str (str): The city string to validate

    Returns:
        str: Normalized city string format "City,State,Country"
    """
    if not city_str:
        logger.warning(f"Empty city string provided, using default")
        return "Louisville,KY,US"

    # Remove any whitespace around commas
    normalized = re.sub(r'\s*,\s*', ',', city_str.strip())

    parts = normalized.split(',')

    # Basic validation
    if len(parts) == 0 or not parts[0]:
        logger.warning(f"Invalid city format: '{city_str}', using default")
        return "Louisville,KY,US"

    # Handle various formats
    if len(parts) == 1:
        # Just city name provided
        logger.info(f"Only city name provided: '{parts[0]}', adding default country code")
        return f"{parts[0]},US"

    elif len(parts) == 2:
        # City and country/state provided
        city, second = parts

        # Special case for US state codes
        if second == "KY" or second in ["NY", "CA", "TX", "FL"]:  # Common US states
            return f"{city},{second},US"

        # Check if second part looks like a country code (2 letters)
        if len(second) == 2:
            # If it's a 2-letter code, could be country or state
            if second.isupper():
                # It's likely a country code, return as is (without adding US)
                return f"{city},{second}"
            elif second.lower() == second:
                # It's likely a lowercase country code, convert to uppercase
                return f"{city},{second.upper()}"
            else:
                # It's likely a US state code, add US
                return f"{city},{second},US"
        # Check if it's a state name
        else:
            # Add US as the default country
            return f"{city},{second},US"

    elif len(parts) >= 3:
        # Full format: City, State, Country
        city, state, country = parts[0], parts[1], parts[2]

        # Normalize country to uppercase (for country codes)
        if len(country) <= 3 and country.isalpha():
            country = country.upper()

        return f"{city},{state},{country}"

    logger.warning(f"Unexpected format: '{city_str}', using as is")
    return normalized
