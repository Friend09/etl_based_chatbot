"""
Chatbot module for the Weather ETL Chatbot application.
Provides natural language interface to weather data using OpenAI's GPT model.
"""

import logging
import json  # noqa: F401 - may be used in future development
from openai import OpenAI

from config.settings import OPENAI_API_KEY, OPENAI_MODEL
from database.db_connector import DatabaseConnector
import pandas as pd  # noqa: F401 - may be used in future development
from datetime import datetime, timedelta  # noqa: F401 - may be used in future development

# Set up logging
logger = logging.getLogger(__name__)

# Initialize OpenAI client
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.error("OpenAI API key not found in environment variables.")
    raise ValueError("API key not found. Please set OPENAI_API_KEY in .env file.")

# Initialize database connector
db = DatabaseConnector()

def get_weather_context():
    """
    Gather relevant weather data to provide context for the AI model.

    Returns:
        str: Context information about weather data
    """
    try:
        # Get current weather
        current_query = """
            SELECT * FROM latest_weather
        """
        current_result = db.execute_query(current_query)

        if not current_result:
            return "No current weather data available."

        # Get forecast
        forecast_query = """
            SELECT * FROM weather_forecasts
            WHERE collection_timestamp = (
                SELECT MAX(collection_timestamp) FROM weather_forecasts
            )
            ORDER BY forecast_timestamp ASC
            LIMIT 8
        """
        forecast_result = db.execute_query(forecast_query)

        # Get historical statistics
        stats_query = """
            SELECT
                DATE(timestamp) as date,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity
            FROM weather_current
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """
        stats_result = db.execute_query(stats_query)

        # Format current weather
        current = current_result[0]
        current_weather = f"""
Current weather in {current[2]} (as of {current[1]}):
- Temperature: {current[3]}°C (feels like {current[4]}°C)
- Conditions: {current[9]} - {current[10]}
- Humidity: {current[5]}%
- Wind: {current[7]} m/s, direction {current[8]}°
- Pressure: {current[6]} hPa
- Visibility: {current[12] if current[12] else 'N/A'} meters
"""

        # Format forecast
        forecast_weather = "Upcoming forecast:\n"
        for forecast in forecast_result:
            forecast_time = forecast[2].strftime("%Y-%m-%d %H:%M")
            forecast_weather += f"""
{forecast_time}:
- Temperature: {forecast[4]}°C (feels like {forecast[5]}°C)
- Conditions: {forecast[10]} - {forecast[11]}
- Probability of precipitation: {(forecast[14] * 100) if forecast[14] else 0}%
- Humidity: {forecast[6]}%
- Wind: {forecast[8]} m/s
"""

        # Format historical stats
        historical = "7-day historical averages:\n"
        for stat in stats_result:
            historical += f"""
{stat[0]}:
- Avg temp: {stat[1]:.1f}°C
- Min temp: {stat[2]}°C
- Max temp: {stat[3]}°C
- Avg humidity: {stat[4]:.1f}%
"""

        # Combine all context
        context = current_weather + "\n" + forecast_weather + "\n" + historical
        return context

    except Exception as e:
        logger.error(f"Error gathering weather context: {e}")
        return "Error retrieving weather data."

def process_query(query):
    """
    Process a natural language query about weather data.

    Args:
        query (str): User's natural language query

    Returns:
        str: Response from the AI model
    """
    try:
        # Get context information about weather
        context = get_weather_context()

        # Prepare system message with context and instructions
        system_message = f"""
You are a weather assistant for Louisville, Kentucky. Answer questions based on the weather data provided.
Here's the current weather and forecast information:

{context}

Respond to the user's question based on this data. If the question cannot be answered using the provided data, politely explain what information is available.
Keep responses concise and focused on the weather data. Provide specific numbers and data points when available.
If you're calculating temperature trends or making comparisons, explain your reasoning briefly.
"""

        # Call OpenAI API
        response = client.chat.completions.create(model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": query}
        ],
        max_tokens=1000,
        temperature=0.7)

        # Extract and return the response
        answer = response.choices[0].message.content.strip()
        return answer

    except Exception as e:
        logger.error(f"Error processing query with OpenAI: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try again later."

def answer_query_without_api(query):
    """
    Fallback function to answer basic weather queries without using the OpenAI API.
    Useful for testing or when API is unavailable.

    Args:
        query (str): User's query

    Returns:
        str: Simple response based on available data
    """
    try:
        # Get current weather data
        current_query = """
            SELECT * FROM latest_weather
        """
        result = db.execute_query(current_query)

        if not result:
            return "I'm sorry, but I don't have any current weather information available."

        current = result[0]

        # Check for common query patterns
        query_lower = query.lower()

        if "temperature" in query_lower:
            return f"The current temperature in {current[2]} is {current[3]}°C and it feels like {current[4]}°C."

        elif "weather" in query_lower or "conditions" in query_lower:
            return f"Current weather conditions in {current[2]}: {current[10]} with a temperature of {current[3]}°C."

        elif "humidity" in query_lower:
            return f"The current humidity in {current[2]} is {current[5]}%."

        elif "wind" in query_lower:
            return f"Current wind in {current[2]} is {current[7]} m/s from direction {current[8]}°."

        elif "pressure" in query_lower:
            return f"The barometric pressure in {current[2]} is {current[6]} hPa."

        elif "rain" in query_lower or "precipitation" in query_lower:
            rain = current[13] if current[13] else 0
            return f"Rainfall in the last hour: {rain} mm."

        else:
            # Default response with general weather info
            return f"""
Current weather in {current[2]}:
Temperature: {current[3]}°C (feels like {current[4]}°C)
Conditions: {current[10]}
Humidity: {current[5]}%
Wind: {current[7]} m/s
"""

    except Exception as e:
        logger.error(f"Error in fallback query processing: {e}")
        return "I'm sorry, I couldn't process your request at the moment."
