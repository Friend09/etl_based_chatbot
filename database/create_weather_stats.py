#!/usr/bin/env python3
"""
Create the weather_stats table in the database.
This script is used to add the weather_stats table which is used by the chatbot.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_connector import DatabaseConnector
from utils.logger import get_component_logger

# Set up logger
logger = get_component_logger('db', 'schema')

def create_weather_stats_table():
    """Create the weather_stats table in the database."""
    logger.info("Creating weather_stats table...")

    db = DatabaseConnector()

    try:
        # Read the SQL file
        schema_file = os.path.join(os.path.dirname(__file__), 'weather_stats.sql')
        with open(schema_file, 'r') as f:
            sql = f.read()

        # Execute the schema SQL statements
        with db.transaction() as cursor:
            cursor.execute(sql)

        logger.info("Weather stats table created successfully")
        return True

    except Exception as e:
        logger.error(f"Failed to create weather stats table: {e}")
        return False

if __name__ == "__main__":
    success = create_weather_stats_table()
    if success:
        print("Weather stats table created successfully!")
    else:
        print("Failed to create weather stats table. Check logs for details.")
        sys.exit(1)
