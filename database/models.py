"""
Database models for the Weather ETL Chatbot application.
Defines SQLAlchemy models for database tables.
"""

import json
from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, String, DateTime,
    Boolean, ForeignKey, Text, JSON, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class WeatherCurrent(Base):
    """Model for current weather data."""

    __tablename__ = 'weather_current'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    city = Column(String(100), nullable=False)
    temperature = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    pressure = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Integer, nullable=False)
    weather_main = Column(String(50), nullable=False)
    weather_description = Column(String(100), nullable=False)
    clouds = Column(Integer, nullable=False)
    visibility = Column(Integer)
    rain_1h = Column(Float)
    snow_1h = Column(Float)
    raw_data = Column(JSON, nullable=False)

    def __repr__(self):
        """String representation of the model."""
        return f"<WeatherCurrent(id={self.id}, timestamp={self.timestamp}, temp={self.temperature})>"

    def to_dict(self):
        """Convert model to dictionary."""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Convert datetime to string
        if result['timestamp']:
            result['timestamp'] = result['timestamp'].isoformat()
        return result


class WeatherForecast(Base):
    """Model for weather forecast data."""

    __tablename__ = 'weather_forecasts'

    id = Column(Integer, primary_key=True)
    collection_timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    forecast_timestamp = Column(DateTime(timezone=True), nullable=False)
    city = Column(String(100), nullable=False)
    temperature = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=False)
    humidity = Column(Integer, nullable=False)
    pressure = Column(Integer, nullable=False)
    wind_speed = Column(Float, nullable=False)
    wind_direction = Column(Integer, nullable=False)
    weather_main = Column(String(50), nullable=False)
    weather_description = Column(String(100), nullable=False)
    clouds = Column(Integer, nullable=False)
    visibility = Column(Integer)
    pop = Column(Float)  # Probability of precipitation
    rain_3h = Column(Float)
    snow_3h = Column(Float)
    raw_data = Column(JSON, nullable=False)

    def __repr__(self):
        """String representation of the model."""
        return f"<WeatherForecast(id={self.id}, forecast_time={self.forecast_timestamp}, temp={self.temperature})>"

    def to_dict(self):
        """Convert model to dictionary."""
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Convert datetimes to strings
        for key in ['collection_timestamp', 'forecast_timestamp']:
            if result[key]:
                result[key] = result[key].isoformat()
        return result


class WeatherReport(Base):
    """Model for daily weather reports."""

    __tablename__ = 'weather_reports'

    id = Column(Integer, primary_key=True)
    report_date = Column(DateTime(timezone=True), nullable=False)
    report_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """String representation of the model."""
        return f"<WeatherReport(id={self.id}, date={self.report_date})>"

    def to_dict(self):
        """Convert model to dictionary."""
        result = {
            'id': self.id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'report_data': self.report_data
        }
        return result


def create_tables(engine):
    """
    Create all tables in the database.

    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)
