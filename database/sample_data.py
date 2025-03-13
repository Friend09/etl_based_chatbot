# database/sample_data.py

"""
Sample data generation script for the Weather ETL Chatbot application.
"""

import logging
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from database.db_utils import upsert_location, upsert_weather_data, DatabaseError
from utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)

# Sample locations
SAMPLE_LOCATIONS = [
    {
        'city_name': 'Louisville',
        'country': 'US',
        'latitude': 38.2527,
        'longitude': -85.7585,
        'population': 615366,
        'timezone': 'America/Kentucky/Louisville'
    },
    {
        'city_name': 'New York',
        'country': 'US',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'population': 8804190,
        'timezone': 'America/New_York'
    },
    {
        'city_name': 'London',
        'country': 'GB',
        'latitude': 51.5074,
        'longitude': -0.1278,
        'population': 8982000,
        'timezone': 'Europe/London'
    }
]

# Weather conditions
WEATHER_CONDITIONS = [
    {'condition': 'Clear', 'description': 'clear sky'},
    {'condition': 'Clouds', 'description': 'few clouds'},
    {'condition': 'Clouds', 'description': 'scattered clouds'},
    {'condition': 'Clouds', 'description': 'broken clouds'},
    {'condition': 'Clouds', 'description': 'overcast clouds'},
    {'condition': 'Rain', 'description': 'light rain'},
    {'condition': 'Rain', 'description': 'moderate rain'},
    {'condition': 'Rain', 'description': 'heavy intensity rain'},
    {'condition': 'Thunderstorm', 'description': 'thunderstorm with light rain'},
    {'condition': 'Thunderstorm', 'description': 'thunderstorm with rain'},
    {'condition': 'Snow', 'description': 'light snow'},
    {'condition': 'Snow', 'description': 'snow'},
    {'condition': 'Mist', 'description': 'mist'},
    {'condition': 'Fog', 'description': 'fog'}
]

def generate_sample_weather(location_id, timestamp):
    """
    Generate random weather data for a location and timestamp.

    Args:
        location_id: ID of the location
        timestamp: Timestamp for the weather data

    Returns:
        Dictionary with weather data
    """
    # Select a random weather condition
    weather = random.choice(WEATHER_CONDITIONS)

    # Generate temperature based on condition
    base_temp = 20  # Base temperature in Celsius
    if weather['condition'] == 'Snow':
        base_temp = -5
    elif weather['condition'] == 'Rain':
        base_temp = 15
    elif weather['condition'] == 'Thunderstorm':
        base_temp = 25

    # Add some randomness to temperature
    temperature = base_temp + random.uniform(-5, 5)

    # Generate other weather attributes
    feels_like = temperature + random.uniform(-2, 2)
    humidity = random.randint(30, 95)
    pressure = random.randint(990, 1030)
    wind_speed = random.uniform(0, 15)
    wind_direction = random.randint(0, 359)
    visibility = random.randint(5000, 10000)
    clouds_percentage = random.randint(0, 100)

    # Generate precipitation based on condition
    precipitation = 0.0
    if weather['condition'] in ['Rain', 'Thunderstorm']:
        precipitation = random.uniform(0.1, 20.0)
    elif weather['condition'] == 'Snow':
        precipitation = random.uniform(0.1, 10.0)

    # Create a mock raw data JSON
    raw_data = {
        'weather': [
            {
                'main': weather['condition'],
                'description': weather['description']
            }
        ],
        'main': {
            'temp': temperature,
            'feels_like': feels_like,
            'humidity': humidity,
            'pressure': pressure
        },
        'wind': {
            'speed': wind_speed,
            'deg': wind_direction
        },
        'clouds': {
            'all': clouds_percentage
        },
        'visibility': visibility,
        'dt': int(timestamp.timestamp())
    }

    return {
        'location_id': location_id,
        'timestamp': timestamp,
        'temperature': temperature,
        'feels_like': feels_like,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'weather_condition': weather['condition'],
        'weather_description': weather['description'],
        'precipitation': precipitation,
        'visibility': visibility,
        'clouds_percentage': clouds_percentage,
        'raw_data': json.dumps(raw_data)
    }

def generate_sample_data(days=30, interval_hours=3):
    """
    Generate sample data for the database.

    Args:
        days: Number of days of historical data to generate
        interval_hours: Interval between weather records in hours

    Returns:
        Number of records created
    """
    try:
        logger.info(f"Generating sample data for {days} days with {interval_hours}h interval")

        location_ids = []
        for location in SAMPLE_LOCATIONS:
            logger.info(f"Adding location: {location['city_name']}, {location['country']}")
            location_id = upsert_location(location)
            location_ids.append(location_id)

        # Generate historical weather data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        current_time = start_time

        weather_count = 0

        while current_time <= end_time:
            for location_id in location_ids:
                weather_data = generate_sample_weather(location_id, current_time)
                upsert_weather_data(weather_data)
                weather_count += 1

            current_time += timedelta(hours=interval_hours)

        logger.info(f"Successfully generated {weather_count} weather records")
        return weather_count

    except DatabaseError as e:
        logger.error(f"Error generating sample data: {e}")
        return 0

def main():
    """
    Main function to run the sample data generation.
    """
    logger.info("Starting sample data generation")

    record_count = generate_sample_data()

    if record_count > 0:
        logger.info(f"Successfully created {record_count} records")
        print(f"Sample data generation completed. Created {record_count} records.")
    else:
        logger.error("Sample data generation failed")
        print("Sample data generation failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
