"""
Utility script to check which OpenWeatherMap APIs are accessible with your API key.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import setup_logger
from utils.location_validator import validate_city_format

# Create a logger
logger = setup_logger("api_checker")

# API endpoints to check
API_ENDPOINTS = [
    {
        "name": "Current Weather API (v2.5)",
        "url": "https://api.openweathermap.org/data/2.5/weather",
        "params": {"q": "London", "appid": "{api_key}", "units": "metric"},
        "description": "Used for current conditions, free tier compatible"
    },
    {
        "name": "5-day/3-hour Forecast API",
        "url": "https://api.openweathermap.org/data/2.5/forecast",
        "params": {"lat": "51.5074", "lon": "-0.1278", "appid": "{api_key}", "units": "metric"},
        "description": "5 days of weather data in 3-hour steps, free tier compatible"
    },
    {
        "name": "OneCall API (v3.0)",
        "url": "https://api.openweathermap.org/data/3.0/onecall",
        "params": {"lat": "51.5074", "lon": "-0.1278", "appid": "{api_key}", "units": "metric"},
        "description": "Comprehensive data, requires 'One Call by Call' subscription"
    },
    {
        "name": "OneCall API (v2.5)",
        "url": "https://api.openweathermap.org/data/2.5/onecall",
        "params": {"lat": "51.5074", "lon": "-0.1278", "appid": "{api_key}", "units": "metric"},
        "description": "Legacy endpoint, requires subscription"
    },
    {
        "name": "16-day Daily Forecast API",
        "url": "https://api.openweathermap.org/data/2.5/forecast/daily",
        "params": {"lat": "51.5074", "lon": "-0.1278", "cnt": "7", "appid": "{api_key}", "units": "metric"},
        "description": "Up to 16 days forecast, requires subscription"
    },
    {
        "name": "Geocoding API (v1.0)",
        "url": "http://api.openweathermap.org/geo/1.0/direct",
        "params": {"q": "London", "limit": "1", "appid": "{api_key}"},
        "description": "Converts city names to coordinates, free tier compatible"
    }
]

def check_api_endpoint(endpoint_data, api_key):
    """
    Check if an API endpoint is accessible with the given API key.

    Args:
        endpoint_data (dict): Data about the endpoint to check
        api_key (str): API key to use

    Returns:
        dict: Result of the check with status and details
    """
    name = endpoint_data["name"]
    url = endpoint_data["url"]
    params = {k: v.replace("{api_key}", api_key) for k, v in endpoint_data["params"].items()}
    description = endpoint_data["description"]

    print(f"\nChecking {name}...")
    print(f"URL: {url}")
    print(f"Description: {description}")

    try:
        # Make the request
        response = requests.get(url, params=params, timeout=10)

        # Check if request was successful
        if response.status_code == 200:
            print(f"✅ Success! API is accessible. Status code: {response.status_code}")
            return {
                "name": name,
                "url": url,
                "status": "success",
                "status_code": response.status_code,
                "data_sample": response.json()
            }
        else:
            print(f"❌ Failed. Status code: {response.status_code}")
            print(f"   Error message: {response.text}")
            return {
                "name": name,
                "url": url,
                "status": "error",
                "status_code": response.status_code,
                "error": response.text
            }
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "name": name,
            "url": url,
            "status": "error",
            "error": str(e)
        }

def check_all_apis():
    """Check all OpenWeatherMap APIs with the API key from environment variables."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("Please set the OPENWEATHERMAP_API_KEY environment variable.")
        print("\nYou can do this by running:")
        print("  export OPENWEATHERMAP_API_KEY=your_api_key_here")
        return

    print("\n=== OpenWeatherMap API Availability Check ===")
    print(f"API Key: {api_key[:4]}...{api_key[-4:]}")
    print("Checking which APIs are accessible with your API key...\n")

    results = []
    accessible_apis = []
    inaccessible_apis = []

    for endpoint in API_ENDPOINTS:
        result = check_api_endpoint(endpoint, api_key)
        results.append(result)

        if result["status"] == "success":
            accessible_apis.append(endpoint["name"])
        else:
            inaccessible_apis.append(endpoint["name"])

    print("\n=== Summary ===")
    print(f"Accessible APIs ({len(accessible_apis)}):")
    for api in accessible_apis:
        print(f"  ✅ {api}")

    print(f"\nInaccessible APIs ({len(inaccessible_apis)}):")
    for api in inaccessible_apis:
        print(f"  ❌ {api}")

    print("\n=== Recommended Configuration ===")
    if "5-day/3-hour Forecast API" in accessible_apis:
        print("✅ Your API key has access to the 5-day/3-hour Forecast API.")
        print("This is the most commonly available API with free tier accounts.")
        print("No changes needed to .env file for basic functionality.")
    else:
        print("❌ Your API key doesn't have access to the 5-day/3-hour Forecast API!")
        print("This is unusual. Please check your API key or OpenWeatherMap account status.")

    # Additional API checks
    if "OneCall API (v3.0)" in accessible_apis:
        print("\n✅ Your API key also has access to the premium OneCall API (v3.0).")
        print("Add to .env file to enable: USE_ONECALL_V3=true")

    if "OneCall API (v2.5)" in accessible_apis:
        print("\n✅ Your API key also has access to the OneCall API (v2.5).")
        print("Add to .env file to enable: USE_ONECALL_V25=true")

    if "16-day Daily Forecast API" in accessible_apis:
        print("\n✅ Your API key also has access to the 16-day Daily Forecast API.")
        print("Add to .env file to enable: USE_DAILY_FORECAST=true")

    # Save detailed results to a file
    output_dir = project_root / "logs"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"api_check_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check OpenWeatherMap API availability")
    args = parser.parse_args()

    check_all_apis()
