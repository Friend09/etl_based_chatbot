"""
Logging constants module.
"""

import logging
import os
from pathlib import Path

# Log file paths
LOG_DIR = Path("logs")
ETL_LOG_FILE = str(LOG_DIR / "etl" / "etl.log")
WEB_LOG_FILE = str(LOG_DIR / "web" / "web.log")
DB_LOG_FILE = str(LOG_DIR / "db" / "db.log")

# Log levels
DEFAULT_LOG_LEVEL = logging.INFO
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
    "production": logging.WARNING,
    "development": logging.DEBUG,
    "testing": logging.DEBUG
}
