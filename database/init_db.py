#!/usr/bin/env python3
"""
Initialize the database for the Weather ETL Chatbot application.
Creates the necessary tables and sets up the database structure.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_connector import DatabaseConnector
from utils.logger import get_component_logger
from database.models import create_tables

# Set up logger
logger = get_component_logger('db', 'init')

def setup_database():
    """Set up the database structure."""
    logger.info("Setting up database")

    db = DatabaseConnector()

    try:
        # Read and execute schema.sql file using proper SQL scripts
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            sql = f.read()

        # Execute the schema SQL (split by ; to execute multiple statements)
        with db.transaction() as cursor:
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)

        logger.info("Database schema created successfully")

        # Optionally, also create SQLAlchemy tables if needed
        # create_tables(engine)
        # logger.info("SQLAlchemy tables created successfully")

        return True
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        return False

def main():
    """Main function to initialize the database."""
    logger.info("Starting database initialization")

    try:
        if setup_database():
            logger.info("Database initialization completed successfully")
            print("Database initialization completed successfully.")
        else:
            logger.error("Database initialization failed")
            print("Database initialization failed. Check logs for details.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
