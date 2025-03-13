"""
Configuration settings for the Weather ETL Chatbot application.
Loads environment variables and provides configuration objects.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenWeatherMap API settings
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
CITY = os.getenv("CITY", "Louisville")
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "US")
LAT = float(os.getenv("LAT", "38.2527"))
LON = float(os.getenv("LON", "-85.7585"))
COLLECTION_INTERVAL = int(os.getenv("COLLECTION_INTERVAL", "3600"))  # Default: 1 hour

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Database settings
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "weather_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Flask application settings
FLASK_CONFIG = {
    "SECRET_KEY": os.getenv("SECRET_KEY", "default-dev-key"),
    "DEBUG": os.getenv("FLASK_DEBUG", "1") == "1",
}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Create logs directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
