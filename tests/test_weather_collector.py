"""
Unit tests for the weather collector module.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from etl.weather_collector import WeatherCollector

class TestWeatherCollector(unittest.TestCase):
    """Test cases for the WeatherCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENWEATHERMAP_API_KEY': 'test_api_key'
        })
        self.env_patcher.start()

        # Create WeatherCollector instance
        self.collector = WeatherCollector()

        # Sample response data
        with open('tests/data/sample_current_weather.json', 'r') as f:
            self.sample_current = json.load(f)

        with open('tests/data/sample_forecast.json', 'r') as f:
            self.sample_forecast = json.load(f)

    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()

    @patch('etl.weather_collector.requests.get')
    def test_fetch_current_weather(self, mock_get):
        """Test fetching current weather data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_current
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        result = self.collector.fetch_current_weather()

        # Verify the result
        self.assertEqual(result, self.sample_current)

        # Check that the request was made with the correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.collector.current_weather_url)
        self.assertEqual(kwargs['params']['appid'], 'test_api_key')
        self.assertEqual(kwargs['params']['lat'], self.collector.lat)
        self.assertEqual(kwargs['params']['lon'], self.collector.lon)

    @patch('etl.weather_collector.requests.get')
    def test_fetch_forecast(self, mock_get):
        """Test fetching forecast data."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_forecast
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the method
        result = self.collector.fetch_forecast()

        # Verify the result
        self.assertEqual(result, self.sample_forecast)

        # Check that the request was made with the correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.collector.forecast_url)
        self.assertEqual(kwargs['params']['appid'], 'test_api_key')

    def test_process_current_weather(self):
        """Test processing current weather data."""
        # Call the method
        result = self.collector.process_current_weather(self.sample_current)

        # Verify the result structure
        self.assertIsInstance(result, dict)
        self.assertIn('timestamp', result)
        self.assertIn('city', result)
        self.assertIn('temperature', result)
        self.assertIn('weather_main', result)
        self.assertIn('raw_data', result)

        # Check specific values
        self.assertEqual(result['city'], self.collector.city)
        self.assertEqual(result['temperature'], self.sample_current['main']['temp'])
        self.assertEqual(result['weather_main'], self.sample_current['weather'][0]['main'])

    def test_process_forecast(self):
        """Test processing forecast data."""
        # Call the method
        result = self.collector.process_forecast(self.sample_forecast)

        # Verify the result structure
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), len(self.sample_forecast['list']))

        # Check the first forecast entry
        first_entry = result[0]
        self.assertIn('forecast_timestamp', first_entry)
        self.assertIn('city', first_entry)
        self.assertIn('temperature', first_entry)
        self.assertIn('weather_main', first_entry)
        self.assertIn('raw_data', first_entry)

        # Check specific values
        self.assertEqual(first_entry['city'], self.collector.city)
        self.assertEqual(first_entry['temperature'], self.sample_forecast['list'][0]['main']['temp'])

    @patch.object(WeatherCollector, 'fetch_current_weather')
    @patch.object(WeatherCollector, 'fetch_forecast')
    @patch.object(WeatherCollector, 'process_current_weather')
    @patch.object(WeatherCollector, 'process_forecast')
    @patch.object(WeatherCollector, 'save_current_weather')
    @patch.object(WeatherCollector, 'save_forecast')
    def test_collect_and_store(self, mock_save_forecast, mock_save_current,
                              mock_process_forecast, mock_process_current,
                              mock_fetch_forecast, mock_fetch_current):
        """Test the complete collection and storage process."""
        # Set up mocks
        mock_fetch_current.return_value = self.sample_current
        mock_fetch_forecast.return_value = self.sample_forecast
        mock_process_current.return_value = {'sample': 'processed_current'}
        mock_process_forecast.return_value = [{'sample': 'processed_forecast'}]
        mock_save_current.return_value = 1
        mock_save_forecast.return_value = 1

        # Call the method
        self.collector.collect_and_store()

        # Verify that all methods were called
        mock_fetch_current.assert_called_once()
        mock_fetch_forecast.assert_called_once()
        mock_process_current.assert_called_once_with(self.sample_current)
        mock_process_forecast.assert_called_once_with(self.sample_forecast)
        mock_save_current.assert_called_once_with({'sample': 'processed_current'})
        mock_save_forecast.assert_called_once_with([{'sample': 'processed_forecast'}])


if __name__ == '__main__':
    unittest.main()
