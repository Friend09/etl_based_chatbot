"""
Main FastAPI application for the Weather ETL Chatbot.
Initializes the FastAPI app, registers routes, and starts the server.
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import uvicorn
from pydantic import BaseModel
import json

from database.db_connector import DatabaseConnector
from config.settings import TEMPLATES_DIR, STATIC_DIR
from utils.logger import get_component_logger, log_structured

# Configure the root logger
logger = get_component_logger('web', 'app')
db = DatabaseConnector()

# Create FastAPI app
app = FastAPI(
    title="Weather ETL Chatbot",
    description="Real-time weather information and intelligent chatbot assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class ChatMessage(BaseModel):
    message: str

def get_weather_info():
    """Get current weather information from the database."""
    query = """
        SELECT
            l.city_name,
            w.temperature,
            w.feels_like,
            w.humidity,
            w.weather_description,
            w.wind_speed,
            w.pressure
        FROM weather_current w
        JOIN locations l ON w.location_id = l.location_id
        ORDER BY w.timestamp DESC
        LIMIT 1
    """
    try:
        result = db.execute_query(query)
        if result:
            return {
                'city': result[0][0],
                'temperature': result[0][1],
                'feels_like': result[0][2],
                'humidity': result[0][3],
                'description': result[0][4],
                'wind_speed': result[0][5],
                'pressure': result[0][6]
            }
    except Exception as e:
        logger.error(f"Error fetching weather info: {e}")
    return None

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main page.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """
    Handle chat messages and return responses.
    """
    try:
        # Convert message to lowercase for easier matching
        user_message = message.message.lower()

        # Get current weather information
        weather_info = get_weather_info()

        if not weather_info:
            return {"response": "I'm sorry, but I couldn't fetch the weather information at the moment."}

        # Handle different types of weather-related queries
        if "temperature" in user_message:
            return {
                "response": f"The current temperature in {weather_info['city']} is {weather_info['temperature']}°C, and it feels like {weather_info['feels_like']}°C"
            }
        elif "humidity" in user_message:
            return {
                "response": f"The current humidity in {weather_info['city']} is {weather_info['humidity']}%"
            }
        elif "wind" in user_message:
            return {
                "response": f"The current wind speed in {weather_info['city']} is {weather_info['wind_speed']} m/s"
            }
        elif "pressure" in user_message:
            return {
                "response": f"The current atmospheric pressure in {weather_info['city']} is {weather_info['pressure']} hPa"
            }
        elif any(word in user_message for word in ["weather", "condition", "forecast"]):
            return {
                "response": f"Current weather in {weather_info['city']}: {weather_info['description']}. " +
                          f"The temperature is {weather_info['temperature']}°C (feels like {weather_info['feels_like']}°C) " +
                          f"with {weather_info['humidity']}% humidity."
            }
        else:
            return {
                "response": "You can ask me about the current temperature, humidity, wind speed, pressure, or general weather conditions. What would you like to know?"
            }

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/weather/current")
async def current_weather():
    """
    Get the latest weather data.
    """
    try:
        # Query the latest weather from the database
        query = """
            SELECT
                weather_id as id,
                timestamp,
                l.city_name as city,
                temperature,
                feels_like,
                humidity,
                pressure,
                wind_speed,
                wind_direction,
                weather_condition as weather_main,
                weather_description,
                clouds_percentage as clouds,
                visibility,
                raw_data
            FROM weather_current w
            JOIN locations l ON w.location_id = l.location_id
            ORDER BY timestamp DESC
            LIMIT 1
        """

        result = db.execute_query(query)

        if not result:
            raise HTTPException(status_code=404, detail="No weather data available")

        # Convert result to dictionary
        columns = ['id', 'timestamp', 'city', 'temperature', 'feels_like', 'humidity',
                  'pressure', 'wind_speed', 'wind_direction', 'weather_main',
                  'weather_description', 'clouds', 'visibility', 'raw_data']

        weather_data = dict(zip(columns, result[0]))

        # Parse timestamp
        weather_data['timestamp'] = weather_data['timestamp'].isoformat()

        return weather_data

    except Exception as e:
        logger.error(f"Error fetching current weather: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/weather/forecast")
async def weather_forecast():
    """
    Get the latest weather forecast.
    """
    try:
        # Query the latest forecast from the database
        query = """
            SELECT
                forecast_id as id,
                prediction_time as collection_timestamp,
                forecast_time as forecast_timestamp,
                l.city_name as city,
                temperature,
                feels_like,
                humidity,
                pressure,
                wind_speed,
                wind_direction,
                weather_condition as weather_main,
                weather_description,
                clouds_percentage as clouds,
                visibility,
                precipitation_probability as pop,
                raw_data
            FROM weather_forecast f
            JOIN locations l ON f.location_id = l.location_id
            WHERE prediction_time = (
                SELECT MAX(prediction_time) FROM weather_forecast
            )
            ORDER BY forecast_time ASC
        """

        result = db.execute_query(query)

        if not result:
            raise HTTPException(status_code=404, detail="No forecast data available")

        # Convert results to list of dictionaries
        columns = ['id', 'collection_timestamp', 'forecast_timestamp', 'city',
                  'temperature', 'feels_like', 'humidity', 'pressure',
                  'wind_speed', 'wind_direction', 'weather_main',
                  'weather_description', 'clouds', 'visibility', 'pop',
                  'raw_data']

        forecast_data = []
        for row in result:
            item = dict(zip(columns, row))
            item['collection_timestamp'] = item['collection_timestamp'].isoformat()
            item['forecast_timestamp'] = item['forecast_timestamp'].isoformat()
            forecast_data.append(item)

        return forecast_data

    except Exception as e:
        logger.error(f"Error fetching weather forecast: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/weather/stats")
async def weather_stats():
    """
    Get statistical information about weather data.
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

        result = db.execute_query(query)

        if not result:
            raise HTTPException(status_code=404, detail="No statistical data available")

        # Convert result to dictionary
        columns = ['avg_temp', 'min_temp', 'max_temp', 'avg_humidity',
                  'avg_wind_speed', 'total_records', 'first_record', 'last_record']

        stats_data = dict(zip(columns, result[0]))

        # Parse timestamps
        if stats_data['first_record']:
            stats_data['first_record'] = stats_data['first_record'].isoformat()
        if stats_data['last_record']:
            stats_data['last_record'] = stats_data['last_record'].isoformat()

        return stats_data

    except Exception as e:
        logger.error(f"Error fetching weather stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def main():
    """Run the FastAPI application."""
    logger.info("Starting the Weather ETL Chatbot web application")
    uvicorn.run(app, host="0.0.0.0", port=5005, reload=True)

if __name__ == "__main__":
    main()
