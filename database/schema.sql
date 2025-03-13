-- Drop tables if they exist
DROP TABLE IF EXISTS weather_forecasts;
DROP TABLE IF EXISTS weather_current;

-- Create table for current weather data
CREATE TABLE weather_current (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(100) NOT NULL,
    temperature FLOAT NOT NULL,
    feels_like FLOAT NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    wind_speed FLOAT NOT NULL,
    wind_direction INTEGER NOT NULL,
    weather_main VARCHAR(50) NOT NULL,
    weather_description VARCHAR(100) NOT NULL,
    clouds INTEGER NOT NULL,
    visibility INTEGER,
    rain_1h FLOAT,
    snow_1h FLOAT,
    raw_data JSONB NOT NULL
);

-- Create index on timestamp for fast queries
CREATE INDEX idx_weather_current_timestamp ON weather_current(timestamp);

-- Create table for weather forecasts
CREATE TABLE weather_forecasts (
    id SERIAL PRIMARY KEY,
    collection_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    forecast_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    city VARCHAR(100) NOT NULL,
    temperature FLOAT NOT NULL,
    feels_like FLOAT NOT NULL,
    humidity INTEGER NOT NULL,
    pressure INTEGER NOT NULL,
    wind_speed FLOAT NOT NULL,
    wind_direction INTEGER NOT NULL,
    weather_main VARCHAR(50) NOT NULL,
    weather_description VARCHAR(100) NOT NULL,
    clouds INTEGER NOT NULL,
    visibility INTEGER,
    pop FLOAT, -- Probability of precipitation
    rain_3h FLOAT,
    snow_3h FLOAT,
    raw_data JSONB NOT NULL
);

-- Create indexes for forecasts table
CREATE INDEX idx_weather_forecasts_collection_timestamp ON weather_forecasts(collection_timestamp);
CREATE INDEX idx_weather_forecasts_forecast_timestamp ON weather_forecasts(forecast_timestamp);

-- Create a view for the latest weather data
CREATE OR REPLACE VIEW latest_weather AS
SELECT *
FROM weather_current
WHERE timestamp = (SELECT MAX(timestamp) FROM weather_current);

-- Comments
COMMENT ON TABLE weather_current IS 'Stores current weather data for Louisville, KY';
COMMENT ON TABLE weather_forecasts IS 'Stores forecast weather data for Louisville, KY';
COMMENT ON COLUMN weather_current.temperature IS 'Temperature in Celsius';
COMMENT ON COLUMN weather_current.feels_like IS 'Feels like temperature in Celsius';
COMMENT ON COLUMN weather_current.wind_speed IS 'Wind speed in meters per second';
COMMENT ON COLUMN weather_current.wind_direction IS 'Wind direction in degrees';
COMMENT ON COLUMN weather_current.raw_data IS 'Original JSON response from OpenWeatherMap API';
