"""
Route definitions for the Weather ETL Chatbot web application.
"""

import logging
import json
from flask import render_template, request, jsonify
from web.chatbot import process_query
from database.db_connector import DatabaseConnector

# Set up logging
logger = logging.getLogger(__name__)
db = DatabaseConnector()

def register_routes(app):
    """
    Register all routes for the application.

    Args:
        app (Flask): Flask application instance
    """

    @app.route('/')
    def index():
        """Render the main page of the application."""
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        """Render the chat interface."""
        return render_template('chat.html')

    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        """
        Process a chat request from the user.

        Returns:
            JSON: Response containing the chatbot's answer
        """
        try:
            # Get user query from request
            data = request.json
            user_query = data.get('query', '')

            if not user_query:
                return jsonify({
                    'error': 'No query provided'
                }), 400

            # Process query and get response
            response = process_query(user_query)

            return jsonify({
                'response': response
            })

        except Exception as e:
            logger.error(f"Error processing chat request: {e}")
            return jsonify({
                'error': 'Internal server error'
            }), 500

    @app.route('/api/weather/current')
    def current_weather():
        """
        Get the latest weather data.

        Returns:
            JSON: Latest weather data
        """
        try:
            # Query the latest weather from the database
            query = """
                SELECT * FROM latest_weather
            """

            result = db.execute_query(query, cursor_factory=None)

            if not result:
                return jsonify({
                    'error': 'No weather data available'
                }), 404

            # Convert result to dictionary
            columns = ['id', 'timestamp', 'city', 'temperature', 'feels_like', 'humidity',
                      'pressure', 'wind_speed', 'wind_direction', 'weather_main',
                      'weather_description', 'clouds', 'visibility', 'rain_1h',
                      'snow_1h', 'raw_data']

            weather_data = dict(zip(columns, result[0]))

            # Parse timestamp
            weather_data['timestamp'] = weather_data['timestamp'].isoformat()

            # Parse JSON data
            if 'raw_data' in weather_data and weather_data['raw_data']:
                weather_data['raw_data'] = json.loads(weather_data['raw_data'])

            return jsonify(weather_data)

        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return jsonify({
                'error': 'Internal server error'
            }), 500

    @app.route('/api/weather/forecast')
    def weather_forecast():
        """
        Get the latest weather forecast.

        Returns:
            JSON: Weather forecast data
        """
        try:
            # Query the latest forecast from the database
            query = """
                SELECT * FROM weather_forecasts
                WHERE collection_timestamp = (
                    SELECT MAX(collection_timestamp) FROM weather_forecasts
                )
                ORDER BY forecast_timestamp ASC
            """

            result = db.execute_query(query, cursor_factory=None)

            if not result:
                return jsonify({
                    'error': 'No forecast data available'
                }), 404

            # Convert results to list of dictionaries
            columns = ['id', 'collection_timestamp', 'forecast_timestamp', 'city',
                      'temperature', 'feels_like', 'humidity', 'pressure',
                      'wind_speed', 'wind_direction', 'weather_main',
                      'weather_description', 'clouds', 'visibility', 'pop',
                      'rain_3h', 'snow_3h', 'raw_data']

            forecast_data = []
            for row in result:
                item = dict(zip(columns, row))

                # Parse timestamps
                item['collection_timestamp'] = item['collection_timestamp'].isoformat()
                item['forecast_timestamp'] = item['forecast_timestamp'].isoformat()

                # Parse JSON data
                if 'raw_data' in item and item['raw_data']:
                    item['raw_data'] = json.loads(item['raw_data'])

                forecast_data.append(item)

            return jsonify(forecast_data)

        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return jsonify({
                'error': 'Internal server error'
            }), 500

    @app.route('/api/weather/stats')
    def weather_stats():
        """
        Get statistical information about weather data.

        Returns:
            JSON: Weather statistics
        """
        try:
            # Query statistical information from the database
            query = """
                SELECT
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp,
                    AVG(humidity) as avg_humidity,
                    AVG(wind_speed) as avg_wind_speed,
                    COUNT(*) as total_records,
                    MIN(timestamp) as first_record,
                    MAX(timestamp) as last_record
                FROM weather_current
            """

            result = db.execute_query(query, cursor_factory=None)

            if not result:
                return jsonify({
                    'error': 'No statistical data available'
                }), 404

            # Convert result to dictionary
            columns = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity',
                      'avg_wind_speed', 'total_records', 'first_record', 'last_record']

            stats_data = dict(zip(columns, result[0]))

            # Parse timestamps
            if stats_data['first_record']:
                stats_data['first_record'] = stats_data['first_record'].isoformat()

            if stats_data['last_record']:
                stats_data['last_record'] = stats_data['last_record'].isoformat()

            return jsonify(stats_data)

        except Exception as e:
            logger.error(f"Error fetching weather statistics: {e}")
            return jsonify({
                'error': 'Internal server error'
            }), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not found'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        return jsonify({
            'error': 'Internal server error'
        }), 500
