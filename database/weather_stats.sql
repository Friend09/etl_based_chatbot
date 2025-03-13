-- Create weather stats table for storing weather statistics and summaries
-- These can be used by the chatbot to provide interesting insights

CREATE TABLE IF NOT EXISTS weather_stats (
    stat_id SERIAL PRIMARY KEY,
    location_id INTEGER REFERENCES locations(location_id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    avg_temperature DECIMAL(5,2),
    min_temperature DECIMAL(5,2),
    max_temperature DECIMAL(5,2),
    avg_humidity INTEGER,
    dominant_condition VARCHAR(100),
    precipitation_days INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_weather_stats_location_id ON weather_stats(location_id);
CREATE INDEX IF NOT EXISTS idx_weather_stats_date_range ON weather_stats(start_date, end_date);

-- Create view for latest stats
CREATE OR REPLACE VIEW latest_weather_stats AS
SELECT s.*
FROM weather_stats s
INNER JOIN (
    SELECT location_id, MAX(end_date) as max_date
    FROM weather_stats
    GROUP BY location_id
) latest ON s.location_id = latest.location_id AND s.end_date = latest.max_date;

-- Add comments
COMMENT ON TABLE weather_stats IS 'Statistical summaries and aggregates of weather data';
COMMENT ON COLUMN weather_stats.start_date IS 'Start date for the statistical period';
COMMENT ON COLUMN weather_stats.end_date IS 'End date for the statistical period';
COMMENT ON COLUMN weather_stats.dominant_condition IS 'Most frequent weather condition in the period';

-- Sample data to get started
INSERT INTO weather_stats (
    location_id, start_date, end_date,
    avg_temperature, min_temperature, max_temperature,
    avg_humidity, dominant_condition, precipitation_days, notes
)
SELECT
    l.location_id,
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE,

    -- Use actual data if available, otherwise use sample values
    COALESCE(
        (SELECT AVG(temperature) FROM weather_current WHERE location_id = l.location_id),
        15.5
    ) AS avg_temperature,

    COALESCE(
        (SELECT MIN(temperature) FROM weather_current WHERE location_id = l.location_id),
        5.2
    ) AS min_temperature,

    COALESCE(
        (SELECT MAX(temperature) FROM weather_current WHERE location_id = l.location_id),
        25.8
    ) AS max_temperature,

    COALESCE(
        (SELECT AVG(humidity) FROM weather_current WHERE location_id = l.location_id),
        65
    ) AS avg_humidity,

    COALESCE(
        (SELECT weather_condition
         FROM weather_current
         WHERE location_id = l.location_id
         GROUP BY weather_condition
         ORDER BY COUNT(*) DESC
         LIMIT 1),
        'Partly Cloudy'
    ) AS dominant_condition,

    5 AS precipitation_days,
    'Monthly weather statistics for the last 30 days' AS notes

FROM locations l
WHERE l.city_name = 'Louisville'
ON CONFLICT DO NOTHING;
