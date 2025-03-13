"""
Unit tests for the data processor module.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from etl.data_processor import WeatherDataProcessor

class TestDataProcessor(unittest.TestCase):
    """Test cases for the WeatherDataProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = WeatherDataProcessor()

        # Sample current weather data
        self.current_data = [
            {
                'timestamp': datetime(2023, 3, 11, 10, 0),
                'city': 'Louisville',
                'temperature': 23.5,
                'feels_like': 22.8,
                'humidity': 45,
                'pressure': 1015,
                'wind_speed': 3.6,
                'wind_direction': 270,
                'weather_main': 'Clear',
                'weather_description': 'clear sky',
                'clouds': 0,
                'visibility': 10000,
                'rain_1h': None,
                'snow_1h': None,
                'raw_data': '{"weather":[{"main":"Clear","description":"clear sky"}]}'
            },
            {
                'timestamp': datetime(2023, 3, 11, 11, 0),
                'city': 'Louisville',
                'temperature': 24.2,
                'feels_like': 23.5,
                'humidity': 42,
                'pressure': 1014,
                'wind_speed': 3.8,
                'wind_direction': 275,
                'weather_main': 'Clear',
                'weather_description': 'clear sky',
                'clouds': 0,
                'visibility': 10000,
                'rain_1h': None,
                'snow_1h': None,
                'raw_data': '{"weather":[{"main":"Clear","description":"clear sky"}]}'
            }
        ]

        # Sample forecast data
        self.forecast_data = [
            {
                'collection_timestamp': datetime(2023, 3, 11, 10, 0),
                'forecast_timestamp': datetime(2023, 3, 11, 15, 0),
                'city': 'Louisville',
                'temperature': 22.8,
                'feels_like': 21.5,
                'humidity': 48,
                'pressure': 1016,
                'wind_speed': 3.9,
                'wind_direction': 280,
                'weather_main': 'Clear',
                'weather_description': 'clear sky',
                'clouds': 0,
                'visibility': 10000,
                'pop': 0,
                'rain_3h': None,
                'snow_3h': None,
                'raw_data': '{"weather":[{"main":"Clear","description":"clear sky"}]}'
            },
            {
                'collection_timestamp': datetime(2023, 3, 11, 10, 0),
                'forecast_timestamp': datetime(2023, 3, 11, 18, 0),
                'city': 'Louisville',
                'temperature': 23.7,
                'feels_like': 22.7,
                'humidity': 45,
                'pressure': 1015,
                'wind_speed': 3.7,
                'wind_direction': 275,
                'weather_main': 'Clear',
                'weather_description': 'clear sky',
                'clouds': 0,
                'visibility': 10000,
                'pop': 0,
                'rain_3h': None,
                'snow_3h': None,
                'raw_data': '{"weather":[{"main":"Clear","description":"clear sky"}]}'
            }
        ]

    def test_process_current_data(self):
        """Test processing current weather data."""
        # Convert sample data to DataFrame
        df = pd.DataFrame(self.current_data)

        # Process the data
        result = self.processor.process_current_data(self.current_data)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

        # Check that new columns were added
        self.assertIn('temperature_f', result.columns)
        self.assertIn('temp_change_1h', result.columns)

        # Check calculations
        # Temperature in Fahrenheit (C to F conversion)
        self.assertAlmostEqual(result.iloc[0]['temperature_f'], 74.3, places=1)  # 23.5°C → ~74.3°F

        # Temperature change
        self.assertAlmostEqual(result.iloc[1]['temp_change_1h'], 0.7, places=1)  # 24.2 - 23.5 = 0.7

    def test_process_forecast_data(self):
        """Test processing forecast data."""
        # Process the data
        result = self.processor.process_forecast_data(self.forecast_data)

        # Verify the result
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)

        # Check that new columns were added
        self.assertIn('hours_until_forecast', result.columns)
        self.assertIn('temperature_f', result.columns)

        # Check calculations
        # Hours until forecast
        self.assertEqual(result.iloc[0]['hours_until_forecast'], 5.0)  # 15:00 - 10:00 = 5 hours
        self.assertEqual(result.iloc[1]['hours_until_forecast'], 8.0)  # 18:00 - 10:00 = 8 hours

    def test_detect_anomalies(self):
        """Test anomaly detection."""
        # Create test data with an anomaly
        data = [
            {'timestamp': '2023-03-10', 'temperature': 20.0},
            {'timestamp': '2023-03-11', 'temperature': 21.0},
            {'timestamp': '2023-03-12', 'temperature': 22.0},
            {'timestamp': '2023-03-13', 'temperature': 40.0},  # Anomaly
            {'timestamp': '2023-03-14', 'temperature': 23.0}
        ]
        df = pd.DataFrame(data)

        # Detect anomalies
        result = self.processor.detect_anomalies(df, 'temperature', window=3, threshold=2.0)

        # Verify the result
        self.assertIn('temperature_zscore', result.columns)
        self.assertIn('temperature_anomaly', result.columns)

        # Check that the anomaly was detected
        self.assertTrue(result.iloc[3]['temperature_anomaly'])  # The 40.0°C reading should be flagged
        self.assertFalse(result.iloc[0]['temperature_anomaly'])  # The 20.0°C reading should not be flagged

    def test_generate_daily_report(self):
        """Test generating a daily report."""
        # Convert sample data to DataFrames
        current_df = pd.DataFrame(self.current_data)
        forecast_df = pd.DataFrame(self.forecast_data)

        # Generate report
        report = self.processor.generate_daily_report(current_df, forecast_df)

        # Verify the result
        self.assertIsInstance(report, dict)
        self.assertIn('report_date', report)
        self.assertIn('current', report)
        self.assertIn('forecast', report)

        # Check current weather data
        self.assertEqual(report['current']['temperature'], 24.2)  # Latest temperature
        self.assertEqual(report['current']['humidity'], 42)

        # Check forecast data
        self.assertIn('daily', report['forecast'])

        # Without testing specific date strings which may vary,
        # ensure some forecast data exists
        self.assertTrue(len(report['forecast']['daily']) > 0)


if __name__ == '__main__':
    unittest.main()
