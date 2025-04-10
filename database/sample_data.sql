-- Insert sample location data
INSERT INTO locations (city_name, country, latitude, longitude)
VALUES ('Louisville', 'US', 38.2527, -85.7585)
ON CONFLICT (city_name, country) DO NOTHING;

-- Insert sample current weather data
INSERT INTO weather_current (
    location_id,
    timestamp,
    temperature,
    feels_like,
    humidity,
    pressure,
    wind_speed,
    wind_direction,
    weather_condition,
    weather_description,
    clouds_percentage,
    visibility,
    raw_data
)
SELECT
    l.location_id,
    CURRENT_TIMESTAMP,
    22.5,  -- temperature in Celsius
    23.0,  -- feels like
    65,    -- humidity percentage
    1015,  -- pressure
    3.5,   -- wind speed
    180,   -- wind direction
    'Clear',
    'Clear sky',
    10,    -- clouds percentage
    10000, -- visibility
    '{"main": {"temp": 22.5, "feels_like": 23.0, "humidity": 65, "pressure": 1015}, "weather": [{"main": "Clear", "description": "clear sky"}]}'::jsonb
FROM locations l
WHERE l.city_name = 'Louisville' AND l.country = 'US';
