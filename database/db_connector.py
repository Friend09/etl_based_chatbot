# database/db_connector.py (updated version)

"""
Database connector module providing connection management for PostgreSQL database.

This module may not be directly imported by all files but serves as the core database
connection layer used by db_utils.py and other components accessing the database.

Provides:
- Connection pooling
- Transaction management
- Error handling for database operations
- Automatic reconnection
"""

# Note: This is a core module used by database utilities and should not be removed.

import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor, Json
import logging
from contextlib import contextmanager
import json
from datetime import datetime
import time  # Make sure time is imported
import random

from config.settings import DB_CONFIG
from utils.logger import get_component_logger, log_db_function, log_structured

# Create a logger for this module
logger = get_component_logger('db', 'connector')

class DatabaseConnectionError(Exception):
    """Exception raised for database connection errors."""
    pass

class DatabaseQueryError(Exception):
    """Exception raised for database query errors."""
    pass

class DatabaseConnector:
    """
    A class to manage connections to the PostgreSQL database.
    Provides methods for executing queries and managing transactions.
    """

    def __init__(self, config=None, max_retries=3, retry_delay=1):
        """
        Initialize the database connector with configuration.

        Args:
            config (dict, optional): Database configuration parameters.
                If None, will use default from settings.
            max_retries (int): Maximum number of connection retry attempts
            retry_delay (float): Delay between retry attempts in seconds
        """
        self.config = config or DB_CONFIG
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._test_connection()

    def _test_connection(self):
        """
        Test the database connection to ensure configuration is valid.

        Raises:
            DatabaseConnectionError: If connection cannot be established
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result and result[0] == 1:
                        logger.debug("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")

    @contextmanager
    @log_db_function
    def get_connection(self):
        """
        Context manager that yields a database connection.
        Automatically closes the connection when exiting the context.
        Implements retry logic for transient connection failures.

        Yields:
            psycopg2.connection: A PostgreSQL database connection

        Raises:
            DatabaseConnectionError: If connection cannot be established after retries
        """
        conn = None
        attempt = 0
        last_error = None

        while attempt < self.max_retries:
            try:
                logger.debug(f"Connecting to the PostgreSQL database (attempt {attempt+1})")
                conn = psycopg2.connect(**self.config)
                yield conn
                return
            except psycopg2.Error as e:
                last_error = e
                logger.warning(f"Database connection error (attempt {attempt+1}): {e}")

                if conn is not None:
                    try:
                        conn.close()
                    except:
                        pass  # Ignore errors on close

                # Add jitter to retry delay to avoid thundering herd
                jitter = random.uniform(0, 0.5)
                retry_wait = self.retry_delay * (2 ** attempt) + jitter
                logger.debug(f"Retrying in {retry_wait:.2f} seconds")
                time.sleep(retry_wait)
                attempt += 1

        # If we get here, all attempts failed
        logger.error(f"All {self.max_retries} connection attempts failed")
        raise DatabaseConnectionError(f"Failed to connect after {self.max_retries} attempts: {last_error}")

    @contextmanager
    def get_cursor(self, cursor_factory=None, named=False):
        """
        Context manager that yields a cursor from a database connection.
        Automatically commits or rolls back transactions when exiting the context.

        Args:
            cursor_factory: The cursor factory to use (e.g., RealDictCursor)
            named (bool): Whether to use a named cursor (for server-side cursors)

        Yields:
            psycopg2.cursor: A PostgreSQL cursor

        Raises:
            DatabaseConnectionError: If connection fails
            DatabaseQueryError: If query execution fails
        """
        with self.get_connection() as conn:
            cursor_name = None
            if named:
                cursor_name = f"named_cursor_{int(time.time())}"

            cursor = conn.cursor(name=cursor_name, cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database transaction error: {e}")
                raise DatabaseQueryError(f"Query execution failed: {e}")
            finally:
                cursor.close()

    @log_db_function
    def execute_query(self, query, params=None, fetch=True, fetch_one=False, cursor_factory=None):
        """
        Execute a SQL query and optionally return results.

        Args:
            query (str): The SQL query to execute
            params (tuple or dict, optional): Parameters for the SQL query
            fetch (bool): Whether to fetch and return results
            fetch_one (bool): Whether to fetch only one result
            cursor_factory: The cursor factory to use

        Returns:
            list or dict or None: Query results if fetch is True, None otherwise

        Raises:
            DatabaseQueryError: If query execution fails
        """
        start_time = time.time()

        with self.get_cursor(cursor_factory=cursor_factory) as cursor:
            try:
                logger.debug(f"Executing query: {query}")
                log_structured(
                    logger,
                    "debug",
                    "db_query_start",
                    query=query,
                    params_type=type(params).__name__ if params else None
                )

                cursor.execute(query, params)

                if fetch:
                    if fetch_one:
                        result = cursor.fetchone()
                    else:
                        result = cursor.fetchall()

                    execution_time = time.time() - start_time
                    row_count = 1 if result and fetch_one else len(result) if result else 0

                    log_structured(
                        logger,
                        "debug",
                        "db_query_complete",
                        execution_time=execution_time,
                        row_count=row_count
                    )

                    return result
                else:
                    execution_time = time.time() - start_time
                    log_structured(
                        logger,
                        "debug",
                        "db_query_complete",
                        execution_time=execution_time,
                        row_count=cursor.rowcount
                    )
                    return None

            except Exception as e:
                execution_time = time.time() - start_time

                log_structured(
                    logger,
                    "error",
                    "db_query_error",
                    error=str(e),
                    execution_time=execution_time
                )

                raise DatabaseQueryError(f"Query execution failed: {e}")

    @log_db_function
    def execute_dict_query(self, query, params=None, fetch_one=False):
        """
        Execute a SQL query and return results as dictionaries.

        Args:
            query (str): The SQL query to execute
            params (tuple or dict, optional): Parameters for the SQL query
            fetch_one (bool): Whether to fetch only one result

        Returns:
            list of dict or dict: Query results as dictionaries

        Raises:
            DatabaseQueryError: If query execution fails
        """
        return self.execute_query(
            query, params, fetch=True, fetch_one=fetch_one, cursor_factory=RealDictCursor
        )

    @log_db_function
    def execute_many(self, query, params_list):
        """
        Execute a batch SQL operation (many executions of the same query).

        Args:
            query (str): The SQL query to execute
            params_list (list): List of parameter tuples or dictionaries

        Returns:
            int: Number of rows affected

        Raises:
            DatabaseQueryError: If batch execution fails
        """
        if not params_list:
            logger.warning("No parameters provided for batch execution")
            return 0

        start_time = time.time()

        with self.get_cursor() as cursor:
            try:
                logger.debug(f"Executing batch query with {len(params_list)} parameter sets")
                log_structured(
                    logger,
                    "debug",
                    "db_batch_start",
                    query=query,
                    batch_size=len(params_list)
                )

                cursor.executemany(query, params_list)

                execution_time = time.time() - start_time

                log_structured(
                    logger,
                    "debug",
                    "db_batch_complete",
                    execution_time=execution_time,
                    row_count=cursor.rowcount
                )

                return cursor.rowcount

            except Exception as e:
                execution_time = time.time() - start_time

                log_structured(
                    logger,
                    "error",
                    "db_batch_error",
                    error=str(e),
                    execution_time=execution_time
                )

                raise DatabaseQueryError(f"Batch execution failed: {e}")

    @log_db_function
    def insert_json_data(self, table, json_data, return_id=False, id_column='id'):
        """
        Insert JSON data into a table.

        Args:
            table (str): Table name to insert into
            json_data (dict): JSON data to insert
            return_id (bool): Whether to return the ID of the inserted row
            id_column (str): Name of the ID column to return

        Returns:
            int or None: ID of the inserted row if return_id is True

        Raises:
            DatabaseQueryError: If insertion fails
        """
        # Ensure json_data is properly sanitized
        if not isinstance(json_data, dict):
            raise ValueError("json_data must be a dictionary")

        # Convert any datetime objects to ISO format strings
        for key, value in json_data.items():
            if isinstance(value, datetime):
                json_data[key] = value.isoformat()

        keys = list(json_data.keys())

        if not keys:
            raise ValueError("json_data dictionary is empty")

        placeholders = [f"%({key})s" for key in keys]
        columns = ", ".join(keys)
        values = ", ".join(placeholders)

        query = f"INSERT INTO {table} ({columns}) VALUES ({values})"

        if return_id:
            query += f" RETURNING {id_column}"

        with self.get_cursor() as cursor:
            try:
                cursor.execute(query, json_data)
                if return_id:
                    result = cursor.fetchone()
                    return result[0]
                return None
            except Exception as e:
                raise DatabaseQueryError(f"JSON data insertion failed: {e}")

    @log_db_function
    def transaction(self):
        """
        Create a transaction context manager for multiple operations.

        Returns:
            TransactionContext: A context manager for a database transaction
        """
        return TransactionContext(self)

    def initialize_schema(self, schema_file=None):
        """
        Initialize the database schema from a SQL file.

        Args:
            schema_file (str, optional): Path to the schema SQL file.
                If None, will use default schema.sql in the database package.

        Returns:
            bool: True if initialization successful

        Raises:
            DatabaseQueryError: If schema initialization fails
        """
        from pathlib import Path

        if schema_file is None:
            # Use default schema file
            schema_file = Path(__file__).parent / "schema.sql"

        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()

            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(schema_sql)

            logger.info("Database schema initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise DatabaseQueryError(f"Schema initialization failed: {e}")

class TransactionContext:
    """
    Context manager for database transactions.
    Allows multiple operations to be performed in a single transaction.
    """

    def __init__(self, db_connector):
        """
        Initialize transaction context.

        Args:
            db_connector: DatabaseConnector instance
        """
        self.db_connector = db_connector
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Enter the transaction context.

        Returns:
            psycopg2.cursor: A PostgreSQL cursor
        """
        self.conn = psycopg2.connect(**self.db_connector.config)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the transaction context.
        Commits the transaction if no exception occurred, otherwise rolls back.

        Args:
            exc_type: Exception type if an exception was raised, None otherwise
            exc_val: Exception value if an exception was raised, None otherwise
            exc_tb: Exception traceback if an exception was raised, None otherwise
        """
        try:
            if exc_type is None:
                # No exception occurred, commit the transaction
                self.conn.commit()
                logger.debug("Transaction committed")
            else:
                # Exception occurred, roll back the transaction
                self.conn.rollback()
                logger.warning(f"Transaction rolled back due to {exc_type.__name__}: {exc_val}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
