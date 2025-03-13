# OpenWeatherMap API Integration Notes

## API Versions

The application uses multiple OpenWeatherMap API endpoints:

1. **Current Weather API** (v2.5)

   - Endpoint: `https://api.openweathermap.org/data/2.5/weather`
   - Used for: Current weather conditions
   - Subscription: Free tier compatible

2. **5-day/3-hour Forecast API** (v2.5)

   - Endpoint: `https://api.openweathermap.org/data/2.5/forecast`
   - Used for: 5 days of weather data in 3-hour steps
   - Subscription: Free tier compatible
   - Default API used for forecasts

3. **OneCall API** (v3.0)

   - Endpoint: `https://api.openweathermap.org/data/3.0/onecall`
   - Used for: Weather forecasts (current + 8 days)
   - Subscription: Requires "One Call by Call" subscription
   - Note: Only used if explicitly enabled

4. **OneCall API** (v2.5)

   - Endpoint: `https://api.openweathermap.org/data/2.5/onecall`
   - Used for: Weather forecasts (fallback option)
   - Subscription: Requires subscription
   - Note: Only used if explicitly enabled

5. **16-day Daily Forecast API** (v2.5)

   - Endpoint: `https://api.openweathermap.org/data/2.5/forecast/daily`
   - Used for: Up to 16 days of daily forecast
   - Subscription: Requires subscription
   - Note: Only used if explicitly enabled

6. **Geocoding API** (v1.0)
   - Endpoint: `http://api.openweathermap.org/geo/1.0/direct`
   - Used for: Converting city names to coordinates
   - Subscription: Free tier compatible

## Implementation

Our application implements a tiered approach:

1. Use 5-day/3-hour Forecast API by default (free tier compatible)
2. Use OneCall API v3.0 only if explicitly enabled and available
3. Use OneCall API v2.5 only if explicitly enabled and available
4. Use 16-day Daily Forecast API only if explicitly enabled and available

## API Response Differences

### 5-day/3-hour Forecast API

- Returns forecast data in 3-hour steps for 5 days (40 data points)
- Our code aggregates this data into daily forecasts
- Available on free tier
- Less granular than OneCall APIs

### OneCall 3.0

- Provides current, hourly (48h), and daily (8 days) in a single call
- Better accuracy and more data points
- Requires paid subscription

### OneCall 2.5

- Provides current, hourly (48h), and daily (7 days) in a single call
- Slightly less accurate than v3.0
- Requires subscription

### 16-day Daily Forecast

- Provides daily forecast for up to 16 days
- Requires subscription

## Environment Variables

Configure which APIs to use by setting these variables in your `.env` file:

```bash
# Default configuration (works with free tier)
# Using only Current Weather and 5-day/3-hour Forecast APIs

# Enable premium APIs if you have subscriptions
USE_ONECALL_V3=true     # Enable OneCall API 3.0
USE_ONECALL_V25=true    # Enable OneCall API 2.5
USE_DAILY_FORECAST=true # Enable 16-day Daily Forecast API
```

## Troubleshooting

If you're unsure which APIs your key has access to, run:

```bash
python -m utils.check_api_availability
```

## Documentation

- [OpenWeatherMap Current Weather API](https://openweathermap.org/current)
- [OpenWeatherMap 5-day/3-hour Forecast API](https://openweathermap.org/forecast5)
- [OpenWeatherMap OneCall API 3.0](https://openweathermap.org/api/one-call-3)
- [OpenWeatherMap OneCall API 2.5](https://openweathermap.org/api/one-call-api)
- [OpenWeatherMap 16-day Daily Forecast API](https://openweathermap.org/forecast16)
- [OpenWeatherMap Geocoding API](https://openweathermap.org/api/geocoding-api)
