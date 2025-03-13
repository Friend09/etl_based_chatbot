-- Database schema for Weather ETL Chatbot application
-- Use double-dash for SQL comments rather than # symbols

-- Drop views first
DROP VIEW IF EXISTS latest_weather;
DROP VIEW IF EXISTS latest_weather_view;

-- Drop tables if they exist in the correct order (to avoid foreign key constraint issues)
-- Use CASCADE to automatically handle dependencies
DROP TABLE IF EXISTS weather_report CASCADE;
DROP TABLE IF EXISTS weather_forecast CASCADE;
DROP TABLE IF EXISTS weather_current CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

-- Create locations table
CREATE TABLE IF NOT EXISTS locations (
    location_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    population INTEGER,
    timezone VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_location UNIQUE(city_name, country)
);

-- Create weather_current table
CREATE TABLE IF NOT EXISTS weather_current (
    weather_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5,2),
    feels_like DECIMAL(5,2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5,2),
    wind_direction INTEGER,
    weather_condition VARCHAR(100),
    weather_description VARCHAR(255),
    precipitation DECIMAL(5,2),
    visibility INTEGER,
    clouds_percentage INTEGER,
    raw_data JSONB
);

-- Create weather_forecast table
CREATE TABLE IF NOT EXISTS weather_forecast (
    forecast_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    forecast_time TIMESTAMP NOT NULL,
    prediction_time TIMESTAMP NOT NULL,
    temperature DECIMAL(5,2),
    feels_like DECIMAL(5,2),
    humidity INTEGER,
    pressure INTEGER,
    wind_speed DECIMAL(5,2),
    wind_direction INTEGER,
    weather_condition VARCHAR(100),
    weather_description VARCHAR(255),
    precipitation_probability DECIMAL(5,2),
    visibility INTEGER,
    clouds_percentage INTEGER
);

-- Create weather_report table
CREATE TABLE IF NOT EXISTS weather_report (
    report_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    report_date DATE NOT NULL,
    avg_temperature DECIMAL(5,2),
    min_temperature DECIMAL(5,2),
    max_temperature DECIMAL(5,2),
    precipitation_total DECIMAL(5,2),
    avg_humidity INTEGER,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_weather_current_location_id ON weather_current(location_id);
CREATE INDEX IF NOT EXISTS idx_weather_current_timestamp ON weather_current(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_forecast_location_id ON weather_forecast(location_id);
CREATE INDEX IF NOT EXISTS idx_weather_forecast_forecast_time ON weather_forecast(forecast_time);
CREATE INDEX IF NOT EXISTS idx_weather_report_location_id ON weather_report(location_id);
CREATE INDEX IF NOT EXISTS idx_weather_report_report_date ON weather_report(report_date);

-- Create view for latest weather data per location
CREATE OR REPLACE VIEW latest_weather AS
SELECT w.*
FROM weather_current w
INNER JOIN (
    SELECT location_id, MAX(timestamp) as max_timestamp
    FROM weather_current
    GROUP BY location_id
) latest ON w.location_id = latest.location_id AND w.timestamp = latest.max_timestamp;

-- Comments
COMMENT ON TABLE locations IS 'Stores location data for weather tracking';
COMMENT ON TABLE weather_current IS 'Stores current weather measurements and conditions for locations';
COMMENT ON TABLE weather_forecast IS 'Stores forecast weather data for locations';
COMMENT ON TABLE weather_report IS 'Stores daily weather report summaries';
COMMENT ON COLUMN weather_current.temperature IS 'Temperature in Celsius';
COMMENT ON COLUMN weather_current.feels_like IS 'Feels like temperature in Celsius';
COMMENT ON COLUMN weather_current.wind_speed IS 'Wind speed in meters per second';
COMMENT ON COLUMN weather_current.wind_direction IS 'Wind direction in degrees';
COMMENT ON COLUMN weather_current.raw_data IS 'Original JSON response from weather API';
