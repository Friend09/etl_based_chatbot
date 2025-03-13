# Project Structure Documentation

This document provides guidance on the organization and purpose of files in the Weather ETL Chatbot project.

## Core Package Structure

- **config/**: Configuration files and settings

  - `logging_config.py`: Logging system configuration (works with logging_constants.py)
  - `settings.py`: Application-wide settings and environment variables

- **database/**: Database connectivity and data access

  - `db_connector.py`: Core database connection manager
  - `db_utils.py`: Helper functions for database operations
  - `schema.sql`: SQL schema for creating tables

- **etl/**: ETL Pipeline components

  - `extract.py`: Data extraction functions
  - `transform.py`: Data transformation and processing
  - `load.py`: Database loading operations
  - `weather_collector.py`: OpenWeatherMap API client
  - `etl_pipeline.py`: Main ETL process orchestrator

- **utils/**: Utility functions used across the application

  - `logger.py`: Logging utility with component-specific loggers
  - `logger_migration.py`: Tools to update logging code
  - `cleanup.py`: Project structure analysis tool

- **web/**: Web application components

  - `app.py`: Flask application entry point
  - `routes.py`: Web routes and endpoints
  - `chatbot.py`: Chatbot interface

- **tests/**: Test cases

  - `test_database.py`: Tests for database functionality
  - `test_logging.py`: Tests for the logging system
  - `test_weather_collector.py`: Tests for API client

- **chatbot/**: Chatbot components
  - `bot.py`: Core chatbot functionality

## Understanding Apparent Duplicate Files

- **Logging Files**: `config/logging_config.py` vs `utils/logger.py`

  - `logging_config.py`: Configures the logging system
  - `logger.py`: Provides logger instances to components

- **Settings Files**: `config/logging_constants.py` vs `config/settings.py`
  - `logging_constants.py`: Constants specific to the logging system
  - `settings.py`: Application-wide settings and configuration

## Files Loaded Dynamically

Some files may appear unused because they are loaded dynamically at runtime rather than through static imports:

- `etl/extract.py`: Loaded dynamically by the ETL pipeline
- `etl/transform.py`: Loaded dynamically by the ETL pipeline
- `etl/load.py`: Loaded dynamically by the ETL pipeline

## Example and Testing Files

- `examples/`: Contains example code demonstrating component usage
- `tests/`: Contains tests for various components
