"""
Unit tests for the chatbot module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from web.chatbot import process_query, get_weather_context, answer_query_without_api

class TestChatbot(unittest.TestCase):
    """Test cases for the chatbot module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a patcher for environment variables
        self.env_patcher = patch.dict('os.environ', {
            'OPENAI_API_KEY': 'test_api_key'
        })
        self.env_patcher.start()

        # Sample weather data
        self.sample_current = [
            (1, '2023-03-11 10:00:00-05:00', 'Louisville', 23.5, 22.8, 45, 1015, 3.6, 270,
             'Clear', 'clear sky', 0, 10000, None, None, json.dumps({
                 "weather": [{"main": "Clear", "description": "clear sky"}],
                 "main": {"temp": 23.5, "feels_like": 22.8, "humidity": 45, "pressure": 1015},
                 "wind": {"speed": 3.6, "deg": 270}
             }))
        ]

        self.sample_forecast = [
            (1, '2023-03-11 10:00:00-05:00', '2023-03-11 15:00:00-05:00', 'Louisville',
             22.8, 21.5, 48, 1016, 3.9, 280, 'Clear', 'clear sky', 0, 10000, 0, None, None,
             json.dumps({
                 "weather": [{"main": "Clear", "description": "clear sky"}],
                 "main": {"temp": 22.8, "feels_like": 21.5, "humidity": 48, "pressure": 1016},
                 "wind": {"speed": 3.9, "deg": 280},
                 "pop": 0
             })),
            (2, '2023-03-11 10:00:00-05:00', '2023-03-11 18:00:00-05:00', 'Louisville',
             23.7, 22.7, 45, 1015, 3.7, 275, 'Clear', 'clear sky', 0, 10000, 0, None, None,
             json.dumps({
                 "weather": [{"main": "Clear", "description": "clear sky"}],
                 "main": {"temp": 23.7, "feels_like": 22.7, "humidity": 45, "pressure": 1015},
                 "wind": {"speed": 3.7, "deg": 275},
                 "pop": 0
             }))
        ]

    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()

    @patch('web.chatbot.db.execute_query')
    def test_get_weather_context(self, mock_execute_query):
        """Test getting weather context for the chatbot."""
        # Set up the mock to return sample data
        mock_execute_query.side_effect = [
            self.sample_current,  # For current weather
            self.sample_forecast,  # For forecast
            []  # For historical stats (empty for simplicity)
        ]

        # Call the function
        context = get_weather_context()

        # Verify the result
        self.assertIsInstance(context, str)
        self.assertIn('Current weather in Louisville', context)
        self.assertIn('Temperature: 23.5°C', context)
        self.assertIn('Upcoming forecast', context)

    @patch('web.chatbot.get_weather_context')
    @patch('web.chatbot.openai.ChatCompletion.create')
    def test_process_query(self, mock_create, mock_get_context):
        """Test processing a query with the OpenAI API."""
        # Set up mocks
        mock_get_context.return_value = "Sample weather context"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is the AI response"
        mock_create.return_value = mock_response

        # Call the function
        result = process_query("What's the weather like today?")

        # Verify the result
        self.assertEqual(result, "This is the AI response")

        # Check that the API was called with the correct parameters
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        self.assertIn("Sample weather context", kwargs['messages'][0]['content'])
        self.assertEqual(kwargs['messages'][1]['content'], "What's the weather like today?")

    @patch('web.chatbot.db.execute_query')
    def test_answer_query_without_api(self, mock_execute_query):
        """Test answering a query without using the OpenAI API."""
        # Set up the mock to return sample data
        mock_execute_query.return_value = self.sample_current

        # Test temperature query
        result = answer_query_without_api("What's the temperature?")
        self.assertIn("23.5°C", result)

        # Test conditions query
        result = answer_query_without_api("How's the weather?")
        self.assertIn("clear sky", result)

        # Test humidity query
        result = answer_query_without_api("What's the humidity?")
        self.assertIn("45%", result)

        # Test wind query
        result = answer_query_without_api("How's the wind?")
        self.assertIn("3.6 m/s", result)

        # Test general query
        result = answer_query_without_api("Tell me about the weather")
        self.assertIn("Temperature", result)
        self.assertIn("Humidity", result)


if __name__ == '__main__':
    unittest.main()
