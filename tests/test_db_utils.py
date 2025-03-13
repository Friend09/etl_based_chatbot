# tests/test_db_utils.py

"""
Unit tests for database utility functions.
"""

import unittest
from unittest.mock import patch, MagicMock
import psycopg2
from datetime import datetime, timedelta

import database.db_utils as db_utils
from database.db_utils import DatabaseError

class TestDatabaseUtils(unittest.TestCase):
    """Test cases for database utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for the get_db_connection context manager
        self.connection_patcher = patch('database.db_utils.get_db_connection')
        self.mock_get_connection = self.connection_patcher.start()

        # Create mock connection and cursor
        self.mock_connection = MagicMock()
        self.mock_cursor = MagicMock()

        # Configure mocks
        self.mock_get_connection.return_value.__enter__.return_value = self.mock_connection
        self.mock_connection.cursor.return_value.__enter__.return_value = self.mock_cursor

        # Sample test data
        self.sample_location = {
            'city_name': 'Louisville',
            'country': 'US',
            'latitude': 38.2527,
            'longitude': -85.7585,
            'population': 615366,
            'timezone': 'America/Kentucky/Louisville'
        }

        self.sample_weather = {
            'location_id': 1,
            'timestamp': datetime.now(),
            'temperature': 23.5,
            'feels_like': 22.8,
            'humidity': 45,
            'pressure': 1015,
            'wind_speed': 3.6,
            'wind_direction': 270,
            'weather_condition': 'Clear',
            'weather_description': 'clear sky',
            'precipitation': 0.0,
            'visibility': 10000,
            'clouds_percentage': 0,
            'raw_data': '{"weather":[{"main":"Clear","description":"clear sky"}]}'
        }

    def tearDown(self):
        """Tear down test fixtures."""
        self.connection_patcher.stop()

    def test_execute_query(self):
        """Test execute_query function."""
        # Configure mock to return some data
        self.mock_cursor.fetchall.return_value = [(1, 'Louisville'), (2, 'New York')]

        # Call the function
        result = db_utils.execute_query("SELECT * FROM locations")

        # Verify the result
        self.assertEqual(result, [(1, 'Louisville'), (2, 'New York')])

        # Verify that execute was called with the correct query
        self.mock_cursor.execute.assert_called_once_with("SELECT * FROM locations", None)

    def test_execute_query_with_params(self):
        """Test execute_query function with parameters."""
        # Configure mock
        self.mock_cursor.fetchall.return_value = [(1, 'Louisville')]

        # Call the function with parameters
        result = db_utils.execute_query("SELECT * FROM locations WHERE city_name = %s", ('Louisville',))

        # Verify the result
        self.assertEqual(result, [(1, 'Louisville')])

        # Verify that execute was called with the correct query and parameters
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM locations WHERE city_name = %s", ('Louisville',))

    def test_execute_query_error(self):
        """Test error handling in execute_query."""
        # Configure mock to raise an exception
        self.mock_cursor.execute.side_effect = psycopg2.Error("Test error")

        # Call the function and check for exception
        with self.assertRaises(DatabaseError):
            db_utils.execute_query("SELECT * FROM locations")

    def test_location_exists(self):
        """Test location_exists function."""
        # Configure mock for existing location
        self.mock_cursor.fetchone.return_value = (1,)

        # Call the function
        result = db_utils.location_exists('Louisville', 'US')

        # Verify the result
        self.assertEqual(result, 1)

        # Configure mock for non-existing location
        self.mock_cursor.fetchone.return_value = None

        # Call the function
        result = db_utils.location_exists('NonExistent', 'XX')

        # Verify the result
        self.assertIsNone(result)

    def test_upsert_location_insert(self):
        """Test upsert_location for insert case."""
        # Configure mock for location_exists to return None (location doesn't exist)
        with patch('database.db_utils.location_exists', return_value=None):
            # Configure mock for execute_query to return a location_id
            with patch('database.db_utils.execute_query', return_value=[(1,)]):
                # Call the function
                result = db_utils.upsert_location(self.sample_location)

                # Verify the result
                self.assertEqual(result, 1)

    def test_upsert_location_update(self):
        """Test upsert_location for update case."""
        # Configure mock for location_exists to return an ID (location exists)
        with patch('database.db_utils.location_exists', return_value=1):
            # Configure mock for execute_query to return a location_id
            with patch('database.db_utils.execute_query', return_value=[(1,)]):
                # Call the function
                result = db_utils.upsert_location(self.sample_location)

                # Verify the result
                self.assertEqual(result, 1)

    def test_upsert_location_missing_field(self):
        """Test upsert_location with missing required field."""
        # Remove a required field
        incomplete_location = self.sample_location.copy()
        del incomplete_location['latitude']

        # Call the function and check for exception
        with self.assertRaises(ValueError):
            db_utils.upsert_location(incomplete_location)

    def test_upsert_weather_data(self):
        """Test upsert_weather_data function."""
        # Configure mock for execute_query to check if record exists
        with patch('database.db_utils.execute_query', side_effect=[None, [(1,)]]):
            # Call the function
            result = db_utils.upsert_weather_data(self.sample_weather)

            # Verify the result
            self.assertEqual(result, 1)

    def test_get_latest_weather(self):
        """Test get_latest_weather function."""
        # Configure mock
        mock_weather = {'weather_id': 1, 'temperature': 23.5}
        with patch('database.db_utils.execute_query_dict', return_value=mock_weather):
            # Call the function
            result = db_utils.get_latest_weather(location_id=1)

            # Verify the result
            self.assertEqual(result, mock_weather)

    def test_get_weather_by_date_range(self):
        """Test get_weather_by_date_range function."""
        # Configure mock
        mock_weather_list = [
            {'weather_id': 1, 'temperature': 23.5},
            {'weather_id': 2, 'temperature': 24.2}
        ]
        with patch('database.db_utils.execute_query_dict', return_value=mock_weather_list):
            # Call the function
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            result = db_utils.get_weather_by_date_range(1, start_date, end_date)

            # Verify the result
            self.assertEqual(result, mock_weather_list)

    def test_get_weather_stats(self):
        """Test get_weather_stats function."""
        # Configure mock
        mock_stats = {
            'avg_temperature': 23.5,
            'min_temperature': 20.1,
            'max_temperature': 26.8,
            'avg_humidity': 45.3,
            'record_count': 24
        }
        with patch('database.db_utils.execute_query_dict', return_value=mock_stats):
            # Call the function
            result = db_utils.get_weather_stats(location_id=1)

            # Verify the result
            self.assertEqual(result, mock_stats)

if __name__ == '__main__':
    unittest.main()
