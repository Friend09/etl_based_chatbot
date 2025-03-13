"""
Database connection manager for the Weather ETL Chatbot application.
Provides a context manager for database connections and cursor operations.
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
import logging
from contextlib import contextmanager
from config.settings import DB_CONFIG

# Import logging utilities
from utils import get_component_logger, log_db_function, log_structured

# Create a logger for this module
logger = get_component_logger('db', 'connector')

class DatabaseConnector:
    """
    A class to manage connections to the PostgreSQL database.
    Provides methods for executing queries and managing transactions.
    """

    def __init__(self, config=None):
        """
        Initialize the database connector with configuration.

        Args:
            config (dict, optional): Database configuration parameters.
                If None, will use default from settings.
        """
        self.config = config or DB_CONFIG

    @contextmanager
    @log_db_function
    def get_connection(self):
        """
        Context manager that yields a database connection.
        Automatically closes the connection when exiting the context.

        Yields:
            psycopg2.connection: A PostgreSQL database connection
        """
        conn = None
        try:
            logger.debug("Connecting to the PostgreSQL database...")
            conn = psycopg2.connect(**self.config)
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn is not None:
                conn.close()
                logger.debug("Database connection closed.")

    @contextmanager
    def get_cursor(self, cursor_factory=None):
        """
        Context manager that yields a cursor from a database connection.
        Automatically commits or rolls back transactions when exiting the context.

        Args:
            cursor_factory: The cursor factory to use (e.g., RealDictCursor)

        Yields:
            psycopg2.cursor: A PostgreSQL cursor
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database transaction error: {e}")
                raise
            finally:
                cursor.close()

    @log_db_function
    def execute_query(self, query, params=None, fetch=True, cursor_factory=None):
        """
        Execute a SQL query and optionally return results.

        Args:
            query (str): The SQL query to execute
            params (tuple or dict, optional): Parameters for the SQL query
            fetch (bool): Whether to fetch and return results
            cursor_factory: The cursor factory to use

        Returns:
            list: Query results if fetch is True, None otherwise
        """
        with self.get_cursor(cursor_factory=cursor_factory) as cursor:
            logger.debug(f"Executing query: {query}")
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return None

    @log_db_function
    def execute_many(self, query, params_list):
        """
        Execute a batch SQL operation (many executions of the same query).

        Args:
            query (str): The SQL query to execute
            params_list (list): List of parameter tuples or dictionaries

        Returns:
            int: Number of rows affected
        """
        with self.get_cursor() as cursor:
            logger.debug(f"Executing batch query: {query}")
            cursor.executemany(query, params_list)
            return cursor.rowcount

    @log_db_function
    def insert_json_data(self, table, json_data, return_id=False):
        """
        Insert JSON data into a table.

        Args:
            table (str): Table name to insert into
            json_data (dict): JSON data to insert
            return_id (bool): Whether to return the ID of the inserted row

        Returns:
            int or None: ID of the inserted row if return_id is True
        """
        keys = list(json_data.keys())
        placeholders = [f"%({key})s" for key in keys]
        columns = ", ".join(keys)
        values = ", ".join(placeholders)

        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        if return_id:
            query += " RETURNING id"

        with self.get_cursor() as cursor:
            cursor.execute(query, json_data)
            if return_id:
                result = cursor.fetchone()
                return result[0]
            return None
