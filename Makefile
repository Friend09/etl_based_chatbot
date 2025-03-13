.PHONY: setup clean clean-logs run run-debug run-info run-warning run-error test install help setup-logging migrate-loggers test-logging example-logging setup-logging-full

# Configuration
PYTHON = python3
VENV = .venv
LOG_DIR = logs
ETL_LOG_DIR = $(LOG_DIR)/etl
WEB_LOG_DIR = $(LOG_DIR)/web
DB_LOG_DIR = $(LOG_DIR)/db
TEST_LOG_DIR = $(LOG_DIR)/tests

# Default target
help:
	@echo "Available targets:"
	@echo "  setup      : Set up the project environment (create directories, install dependencies)"
	@echo "  clean      : Remove all generated files and directories"
	@echo "  clean-logs : Remove only log files"
	@echo "  run        : Run the application with default logging level (INFO)"
	@echo "  run-debug  : Run the application with DEBUG logging level"
	@echo "  run-info   : Run the application with INFO logging level"
	@echo "  run-warning: Run the application with WARNING logging level"
	@echo "  run-error  : Run the application with ERROR logging level"
	@echo "  test       : Run tests with appropriate logging level"
	@echo "  install    : Install or update dependencies"

# Setup project environment
setup: create-dirs install

# Create necessary directories
create-dirs:
	@echo "Creating necessary directories..."
	@mkdir -p $(LOG_DIR) $(ETL_LOG_DIR) $(WEB_LOG_DIR) $(DB_LOG_DIR) $(TEST_LOG_DIR) data

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
	fi
	@. $(VENV)/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully."

# Clean up generated files and directories
clean: clean-logs
	@echo "Cleaning up..."
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@echo "Clean up completed."

# Clean up log files
clean-logs:
	@echo "Cleaning log files..."
	@rm -f $(LOG_DIR)/*.log $(ETL_LOG_DIR)/*.log $(WEB_LOG_DIR)/*.log $(DB_LOG_DIR)/*.log $(TEST_LOG_DIR)/*.log
	@echo "Log files cleaned up."

# Run the application with default (INFO) log level
run: create-dirs
	@echo "Running application with INFO log level..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=INFO $(PYTHON) main.py

# Run with DEBUG log level
run-debug: create-dirs
	@echo "Running application with DEBUG log level..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=DEBUG $(PYTHON) main.py

# Run with INFO log level
run-info: create-dirs
	@echo "Running application with INFO log level..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=INFO $(PYTHON) main.py

# Run with WARNING log level
run-warning: create-dirs
	@echo "Running application with WARNING log level..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=WARNING $(PYTHON) main.py

# Run with ERROR log level
run-error: create-dirs
	@echo "Running application with ERROR log level..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=ERROR $(PYTHON) main.py

# Run tests with appropriate logging
test: create-dirs
	@echo "Running tests with logging configuration..."
	@. $(VENV)/bin/activate && PYTHONPATH=. LOG_LEVEL=DEBUG TEST_MODE=1 $(PYTHON) -m pytest tests/ -v

# Create a new config/logging_constants.py file target
create-logging-constants:
	@echo "Creating logging constants file..."
	@if [ ! -f "config/logging_constants.py" ]; then \
		mkdir -p config; \
		echo '"""' > config/logging_constants.py; \
		echo 'Logging constants module.' >> config/logging_constants.py; \
		echo '"""' >> config/logging_constants.py; \
		echo '' >> config/logging_constants.py; \
		echo 'import logging' >> config/logging_constants.py; \
		echo 'import os' >> config/logging_constants.py; \
		echo 'from pathlib import Path' >> config/logging_constants.py; \
		echo '' >> config/logging_constants.py; \
		echo '# Log file paths' >> config/logging_constants.py; \
		echo 'LOG_DIR = Path("logs")' >> config/logging_constants.py; \
		echo 'ETL_LOG_FILE = str(LOG_DIR / "etl" / "etl.log")' >> config/logging_constants.py; \
		echo 'WEB_LOG_FILE = str(LOG_DIR / "web" / "web.log")' >> config/logging_constants.py; \
		echo 'DB_LOG_FILE = str(LOG_DIR / "db" / "db.log")' >> config/logging_constants.py; \
		echo '' >> config/logging_constants.py; \
		echo '# Log levels' >> config/logging_constants.py; \
		echo 'DEFAULT_LOG_LEVEL = logging.INFO' >> config/logging_constants.py; \
		echo 'LOG_LEVELS = {' >> config/logging_constants.py; \
		echo '    "debug": logging.DEBUG,' >> config/logging_constants.py; \
		echo '    "info": logging.INFO,' >> config/logging_constants.py; \
		echo '    "warning": logging.WARNING,' >> config/logging_constants.py; \
		echo '    "error": logging.ERROR,' >> config/logging_constants.py; \
		echo '    "critical": logging.CRITICAL,' >> config/logging_constants.py; \
		echo '    "production": logging.WARNING,' >> config/logging_constants.py; \
		echo '    "development": logging.DEBUG,' >> config/logging_constants.py; \
		echo '    "testing": logging.DEBUG' >> config/logging_constants.py; \
		echo '}' >> config/logging_constants.py; \
	fi

# Logging system setup and configuration targets
# Add these to your existing Makefile

# Create necessary directories for logging
setup-logging:
	@echo "Setting up logging system..."
	mkdir -p logs utils
	@echo "Created logs directory"
	@touch logs/.gitkeep
	@echo "Logging system setup complete"

# Run the automated logger migration tool
migrate-loggers:
	@echo "Migrating existing loggers to new logging system..."
	python -m utils.logger_migration
	@echo "Logger migration complete"

# Run logging tests
test-logging:
	@echo "Running logging system tests..."
	python -m unittest tests.test_logging
	@echo "Logging tests complete"

# Run logging example to verify functionality
example-logging:
	@echo "Running logging example script..."
	python examples/logging_example.py
	@echo "Example complete. Check logs directory for output."

# Combined target for full logging setup
setup-logging-full: setup-logging migrate-loggers test-logging example-logging
	@echo "Logging system fully set up and tested"
