# Weather ETL Chatbot

A comprehensive data pipeline and chatbot application that collects weather data for Louisville, KY, stores it in a PostgreSQL database, and provides a natural language interface for querying the data.

## Features

- Automated ETL pipeline for weather data collection using OpenWeatherMap API
- PostgreSQL database for data storage and retrieval
- Flask-based web application with chatbot interface
- Natural language processing using OpenAI's GPT-4o-mini
- Comprehensive logging system with environment-based configurations
- Sensitive information masking in logs
- Data transformation and validation system
- Unit tests for all major components

## Project Structure

```
weather_etl_chatbot/
├── config/          # Configuration files including logging config
├── database/        # Database utilities and scripts
├── dev/             # Other dev related scripts
├── etl/             # ETL pipeline code
│   ├── __init__.py
│   ├── weather_collector.py  # OpenWeatherMap API client
│   ├── data_extractor.py     # Data extraction module
│   ├── data_transformer.py   # Data transformation module
│   ├── data_loader.py        # Data loading utilities
├── files/           # any misc project related files
├── logs/            # Log files directory
├── notebooks/       # Jupyter notebooks for data analysis
├── notes/           # Notes and documentation
├── utils/           # Utilities including logging helpers
│   ├── __init__.py
│   ├── logger.py             # Component-specific loggers
│   └── logger_migration.py   # Tool to migrate existing loggers
├── web/             # Flask web application
│   ├── __init__.py
│   ├── app.py                # Flask application entry point
│   ├── chatbot.py            # Chatbot logic
│   ├── routes.py             # Flask routes
│   └── templates/            # HTML templates
│       ├── index.html
│       └── chat.html
└── tests/           # Test cases
    ├── __init__.py
    ├── test_weather_collector.py  # Tests for weather collector
    ├── test_data_transformer.py   # Tests for data transformation
    ├── test_data_loader.py        # Tests for data loading
    └── test_config.py             # Tests for configuration module
```

### Directory Structure

The project is organized into several main components:

- **etl/**: Contains the ETL (Extract, Transform, Load) pipeline code for collecting and processing weather data
  - `weather_collector.py`: Client for the OpenWeatherMap API
  - `data_extractor.py`: Module to extract data from API responses
  - `data_transformer.py`: Module for validating and transforming extracted data
  - `data_loader.py`: Module for loading processed data into the database
- **web/**: Contains the Flask web application and chatbot interface
- **database/**: Contains database utilities and schema scripts
- **config/**: Contains configuration modules and settings
- **utils/**: Contains utility functions and classes
  - `logger.py`: Advanced logging system with component-specific loggers
  - `logger_migration.py`: Tool to migrate existing loggers
- **tests/**: Contains unit tests for all major components

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/weather_etl_chatbot.git
   cd weather_etl_chatbot
   ```

2. Create and activate a virtual environment:

   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:

   ```
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=weather_db
   DB_USER=postgres
   DB_PASSWORD=your_password

   # API Keys
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
   OPENAI_API_KEY=your_openai_api_key

   # Flask Configuration
   FLASK_SECRET_KEY=your_secret_key
   FLASK_ENV=development
   ```

5. Initialize the database:
   ```
   python3 -m database.init_db
   ```

## Usage

### Available Commands

Here's a comprehensive list of available commands you can use in this framework:

#### Database Commands

```bash
# Initialize the database with schema
python3 -m database.init_db

# Test database connectivity and view table contents
python3 -m tests.test_database
```

#### ETL Pipeline Commands

```bash
# Run the complete ETL pipeline (extract, transform, load)
python3 -m etl.etl_pipeline

# Only collect weather data from API and save to files/database
python3 -m etl.weather_collector

# Run data extraction operations only
python3 -m etl.extract

# Run data transformation operations only
python3 -m etl.transform

# Run data loading operations only
python3 -m etl.load
```

#### Running Individual ETL Components

Each ETL component can be run independently for testing or targeted processing:

```bash
# Extract data from a file with preview
python3 -m etl.extract data/weather/current_20250313.json --preview

# Expected output:
# Extracting data from file: data/weather/current_20250313.json
#
# Data Preview (Dict):
#   coord: {'lon': -85.7585, 'lat': 38.2527}
#   weather: [{'id': 501, 'main': 'Rain', 'description': 'moderate rain', 'icon': '10d'}]
#   base: stations
#   main: {'temp': 12.67, 'feels_like': 11.59, 'temp_min': 10.07, 'temp_max': 14.95, 'pressure': 1011, 'humidity': 58}
#   ... and 9 more items
# Extraction completed successfully

# Extract data from a URL
python3 -m etl.extract --url https://api.openweathermap.org/data/2.5/weather?q=Louisville,KY,US&appid=YOUR_API_KEY&units=metric

# Transform data using the transform module
python3 -m etl.transform data/weather/current_20250313.json --preview

# Load data to the database
python3 -m etl.load data/weather/current_20250313.json --table weather_current

# Extract and save to a new file
python3 -m etl.extract data/weather/current_20250313.json -o data/processed/weather_data.json
```

#### Extract Module Options

The extract module provides several options:

```bash
# Show help
python3 -m etl.extract --help

# Extract from file
python3 -m etl.extract path/to/file.json

# Extract from URL
python3 -m etl.extract --url https://api.example.com/data

# Extract with preview
python3 -m etl.extract path/to/file.json --preview

# Extract and save output
python3 -m etl.extract path/to/file.json --output path/to/output.json
```

#### Web Application Commands

```bash
# Start the Flask web application
python3 -m web.app

# Start the API server only (if implemented separately)
python3 -m web.api
```

#### Utility Commands

```bash
# Check project structure for potential issues
python3 -m utils.cleanup

# Test the logger configuration
python3 -m utils.logger_diagnostic

# Check API key availability
python3 -m utils.check_api_key

# Validate OpenWeatherMap API availability
python3 -m utils.check_api_availability
```

#### Testing Commands

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/test_database.py
pytest tests/test_weather_collector.py
pytest tests/test_logging.py

# Run tests with coverage report
pytest --cov=.
```

#### Environment Variables

You can customize command behavior with environment variables:

```bash
# Use a specific city for weather data
WEATHER_CITY="Miami,FL,US" python3 -m etl.weather_collector

# Specify number of forecast days
FORECAST_DAYS=7 python3 -m etl.etl_pipeline

# Use a specific OpenWeatherMap API key for a single run
OPENWEATHERMAP_API_KEY=your_api_key python3 -m etl.weather_collector

# Set log level for a single run
LOG_LEVEL=DEBUG python3 -m etl.etl_pipeline
```

### Running the ETL Pipeline

To manually run the ETL pipeline:

```
python3 -m etl.run_pipeline
```

To run the complete ETL pipeline that extracts, transforms, loads, and generates reports:

```
python3 -m etl.run_pipeline
```

### Starting the Web Application

To start the Flask web application:

```
python3 -m web.app
```

Then navigate to `http://localhost:5000` in your browser.

## Testing

Run the test suite with:

```
pytest
```

Run specific tests with:

```
pytest tests/test_weather_collector.py
pytest tests/test_data_transformer.py
```

### Testing Database Connectivity

To verify database connectivity and view available tables:

```bash
python3 -m tests.test_database
```

This will:

1. Test the connection to the PostgreSQL database
2. List the available tables
3. Show a sample of the data contained in the database

# Logging System Documentation

## Overview

This logging system provides a comprehensive, centralized approach to logging for the weather ETL and chatbot application. It's designed to provide detailed logs for debugging while keeping sensitive information secure.

## Features

- Environment-based log levels (development, testing, production)
- Component-specific logging (ETL, web app, database)
- File and console handlers
- Automatic log rotation
- Sensitive information masking
- Function call logging with decorators
- Structured logging for log aggregation systems

## Directory Structure

```
├── config
│   └── logging_config.py     # Core logging configuration
├── utils
│   ├── __init__.py           # Utility package initialization
│   ├── logger.py             # Component-specific loggers
│   └── logger_migration.py   # Tool to migrate existing loggers
├── logs                      # Directory for log files
└── tests
    └── test_logging.py       # Unit tests for the logging system
```

## Usage Examples

### Basic Logger Usage

```python
from utils.logger import get_component_logger

# Create a logger for an ETL component
logger = get_component_logger('etl', 'data_transformer')

# Log messages at different levels
logger.debug("Processing record %s", record_id)
logger.info("Transformation complete: %d records processed", count)
logger.warning("Missing value detected in field: %s", field_name)
logger.error("Failed to transform record: %s", error_message)
```

### Using Function Logging Decorators

```python
from utils.logger import log_function_call

@log_function_call
def transform_weather_data(raw_data):
    # Function implementation
    return transformed_data
```

### Structured Logging

```python
logger.info("Data transformation stats", extra={
    'records_processed': 100,
    'records_valid': 95,
    'records_invalid': 5,
    'processing_time_ms': 235
})
```

### Sensitive Data Handling

The logging system automatically masks sensitive information in logs, including:

- API keys
- Passwords
- Tokens
- Secrets
- Credentials

Example before masking:

```
Making request with api_key='abc123' and password='secret'
```

Example after masking:

```
Making request with api_key=***** and password=*****
```

## Log File Organization

The system creates separate log files for different components:

- `app.log` - General application logs
- `etl.log` - ETL process logs
- `web.log` - Web application logs
- `db.log` - Database operation logs

### Example Log Output

```
2023-07-15 14:23:45,123 - etl.data_transformer - INFO - Starting data transformation for batch #12345
2023-07-15 14:23:45,234 - etl.data_transformer - DEBUG - Validating record structure for record ID: wx_20230715_1422
2023-07-15 14:23:45,345 - etl.data_transformer - WARNING - Missing humidity value, using default
2023-07-15 14:23:45,456 - etl.data_transformer - INFO - Transformation complete: 24 records processed in 1.23 seconds
```

## Troubleshooting

If logs are not appearing as expected:

1. Check log level settings in your `.env` file
2. Verify the logs directory exists and is writable
3. Confirm that the logger is being imported correctly
4. Check that the component type is correctly specified

For more help, run the logger diagnostic tool:

```
python3 -m utils.logger_diagnostic
```

## Database Setup and Usage

### Database Schema

The application uses a PostgreSQL database with the following main tables:

- `locations`: Stores location data including city name, country, coordinates
- `weather_current`: Stores current weather measurements linked to locations
- `weather_forecast`: Stores weather forecast data for locations
- `weather_report`: Stores daily compiled weather reports

The database uses SQLAlchemy ORM models for data mapping and schema definition.

### Setting Up the Database

To initialize the database:

```bash
# Create the database in PostgreSQL first
createdb -U postgres weather_db

# Then run the initialization script
python3 -m database.init_db
```

If you encounter any issues, check the log files in the logs/db directory for detailed error messages.

#### Database Schema

The schema setup creates several tables:

- `locations`: Geographic locations for weather data
- `weather_current`: Current weather observations
- `weather_forecast`: Future weather predictions
- `weather_report`: Daily weather summaries and statistics

You can view the complete schema in the `database/schema.sql` file.

### Database Connectivity

The application provides a robust database connection manager with transaction support:

```python
# Import the connector
from database.db_connector import DatabaseConnector

# Create a connector instance
db = DatabaseConnector()

# Execute a query with automatic connection management
results = db.execute_query(
    "SELECT * FROM locations WHERE city_name = %s",
    ("Louisville",)
)

# Use a transaction for multiple operations
with db.transaction() as cursor:
    cursor.execute("INSERT INTO locations (city_name, country) VALUES (%s, %s)",
                  ('Louisville', 'US'))
    location_id = cursor.fetchone()['id']

    # Second operation in same transaction
    cursor.execute(
        "INSERT INTO weather_current (location_id, temperature) VALUES (%s, %s)",
        (location_id, 72.5)
    )
```

### Error Handling

The connector provides specialized error handling for database operations:

```python
from database.db_connector import DatabaseConnectionError, DatabaseQueryError

try:
    results = db.execute_query("SELECT * FROM invalid_table")
except DatabaseQueryError as e:
    logger.error("Query error: %s", e)
except DatabaseConnectionError as e:
    logger.error("Connection error: %s", e)
```

The database connector automatically implements:

- Connection pooling for performance
- Retry logic for transient failures
- Parameter sanitization for security
- Structured logging of database operations
- Transaction management with context managers

## Troubleshooting

### Missing weather_stats Table

If you see errors about the missing `weather_stats` table when running the web application, you need to create this table:

```bash
python3 -m database.create_weather_stats
```

### OpenAI API Version

The chatbot uses the OpenAI API. If you see errors like this:
