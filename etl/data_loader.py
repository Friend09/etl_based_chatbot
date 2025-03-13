"""Module for loading processed weather data into the database."""

import logging
from typing import Dict, List, Any
from sqlalchemy.exc import SQLAlchemyError

from database.db_connector import DatabaseConnector
from database.models import Location, WeatherData

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads processed weather data into the database."""

    def __init__(self):
        """Initialize the data loader."""
        self.db = DatabaseConnector()
        logger.info("Data loader initialized")

    def load_weather_data(self, processed_data: List[Dict[str, Any]]) -> int:
        """Load processed weather data into the database.

        Args:
            processed_data: List of processed weather data dictionaries

        Returns:
            Number of records successfully loaded
        """
        logger.info(f"Loading {len(processed_data)} weather records into database")
        records_loaded = 0

        session = self.db.get_session()
        try:
            for data in processed_data:
                location_data = data.get('location', {})
                weather_data = data.get('weather', {})

                # Get or create location
                location = self._get_or_create_location(session, location_data)

                # Create weather data record
                weather_record = WeatherData(
                    location_id=location.id,
                    temperature=weather_data.get('temperature'),
                    humidity=weather_data.get('humidity'),
                    pressure=weather_data.get('pressure'),
                    wind_speed=weather_data.get('wind_speed'),
                    wind_direction=weather_data.get('wind_direction'),
                    condition=weather_data.get('condition'),
                    precipitation=weather_data.get('precipitation'),
                    cloud_cover=weather_data.get('cloud_cover'),
                    uv_index=weather_data.get('uv_index'),
                    timestamp=weather_data.get('timestamp')
                )

                session.add(weather_record)
                records_loaded += 1

            session.commit()
            logger.info(f"Successfully loaded {records_loaded} weather records")

        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error while loading weather data: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading weather data: {e}")
            raise
        finally:
            self.db.close_session(session)

        return records_loaded

    def _get_or_create_location(self, session, location_data: Dict[str, Any]) -> Location:
        """Get existing location or create a new one.

        Args:
            session: Database session
            location_data: Location data dictionary

        Returns:
            Location object
        """
        name = location_data.get('name')
        country = location_data.get('country')

        # Try to find existing location
        location = session.query(Location).filter_by(
            name=name,
            country=country
        ).first()

        # Create new location if not found
        if not location:
            location = Location(
                name=name,
                country=country,
                latitude=location_data.get('latitude'),
                longitude=location_data.get('longitude')
            )
            session.add(location)
            session.flush()  # Flush to get the ID
            logger.info(f"Created new location: {name}, {country}")

        return location
