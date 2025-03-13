"""
Configuration settings for the Weather ETL Chatbot application.
Loads settings from environment variables and provides defaults.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')

# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

# Set up logging level based on environment variable
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'weather_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# API keys
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# OpenAI model configuration
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))

# Directory paths
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
ETL_LOG_DIR = os.path.join(LOG_DIR, 'etl')
WEB_LOG_DIR = os.path.join(LOG_DIR, 'web')
DB_LOG_DIR = os.path.join(LOG_DIR, 'db')
TEST_LOG_DIR = os.path.join(LOG_DIR, 'test')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, 'web', 'templates')
STATIC_DIR = os.path.join(PROJECT_ROOT, 'web', 'static')

# Create necessary directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ETL_LOG_DIR, exist_ok=True)
os.makedirs(WEB_LOG_DIR, exist_ok=True)
os.makedirs(DB_LOG_DIR, exist_ok=True)
os.makedirs(TEST_LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Application settings
APP_ENV = os.getenv('APP_ENV', 'development')
DEBUG = APP_ENV == 'development'

# Web application settings
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-dev')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')

# Flask configuration dictionary
FLASK_CONFIG = {
    'SECRET_KEY': FLASK_SECRET_KEY,
    'DEBUG': DEBUG,
    'TEMPLATES_AUTO_RELOAD': True if DEBUG else False,
    'EXPLAIN_TEMPLATE_LOADING': True if DEBUG else False,
    'JSON_SORT_KEYS': False,
    'JSONIFY_PRETTYPRINT_REGULAR': True if DEBUG else False,
    'PREFERRED_URL_SCHEME': 'http'
}
