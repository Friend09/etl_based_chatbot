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
   python -m venv venv
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
   python -m database.init_db
   ```

## Usage

### Running the ETL Pipeline

To manually run the ETL pipeline:

```
python -m etl.run_pipeline
```

### Starting the Web Application

To start the Flask web application:

```
python -m web.app
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
python -m utils.logger_diagnostic
```
