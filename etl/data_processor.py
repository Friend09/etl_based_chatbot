"""
Data processor module for the Louisville weather ETL pipeline.
Processes and transforms weather data for analysis and storage.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)

class WeatherDataProcessor:
    """
    Class to process and transform weather data.
    Handles both current weather and forecast data.
    """

    def __init__(self):
        """Initialize the weather data processor."""
        pass

    def process_current_data(self, data_list):
        """
        Process a list of current weather data entries.

        Args:
            data_list (list): List of dictionaries containing weather data

        Returns:
            pandas.DataFrame: Processed data as a DataFrame
        """
        if not data_list:
            logger.warning("No current weather data to process")
            return pd.DataFrame()

        try:
            # Convert to DataFrame
            df = pd.DataFrame(data_list)

            # Convert timestamp to datetime if it's not already
            if 'timestamp' in df.columns and not pd.api.types.is_datetime64_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])

            # Sort by timestamp
            df.sort_values('timestamp', inplace=True)

            # Create additional features
            if 'temperature' in df.columns:
                # Convert temperature to Fahrenheit if needed
                if 'temperature_f' not in df.columns:
                    df['temperature_f'] = df['temperature'] * 9/5 + 32

                # Calculate temperature changes
                df['temp_change_1h'] = df['temperature'].diff()
                df['temp_change_24h'] = df['temperature'] - df['temperature'].shift(24)  # Assuming hourly data

            # Calculate humidity-related features
            if 'humidity' in df.columns:
                df['humidity_change_1h'] = df['humidity'].diff()

                # Calculate heat index when temperature > 80°F (26.7°C) and humidity > 40%
                mask = (df['temperature_f'] > 80) & (df['humidity'] > 40)
                df['heat_index_f'] = np.nan

                # Heat index formula (simplified)
                df.loc[mask, 'heat_index_f'] = -42.379 + \
                                               2.04901523 * df.loc[mask, 'temperature_f'] + \
                                               10.14333127 * df.loc[mask, 'humidity'] / 100 - \
                                               0.22475541 * df.loc[mask, 'temperature_f'] * df.loc[mask, 'humidity'] / 100 - \
                                               0.00683783 * df.loc[mask, 'temperature_f'] ** 2 - \
                                               0.05481717 * (df.loc[mask, 'humidity'] / 100) ** 2 + \
                                               0.00122874 * df.loc[mask, 'temperature_f'] ** 2 * df.loc[mask, 'humidity'] / 100 + \
                                               0.00085282 * df.loc[mask, 'temperature_f'] * (df.loc[mask, 'humidity'] / 100) ** 2 - \
                                               0.00000199 * df.loc[mask, 'temperature_f'] ** 2 * (df.loc[mask, 'humidity'] / 100) ** 2

                # Convert to Celsius
                df['heat_index'] = (df['heat_index_f'] - 32) * 5/9

            # Calculate wind chill when temperature < 50°F (10°C) and wind speed > 3 mph (1.34 m/s)
            if 'temperature' in df.columns and 'wind_speed' in df.columns:
                wind_speed_mph = df['wind_speed'] * 2.237  # Convert m/s to mph
                mask = (df['temperature_f'] < 50) & (wind_speed_mph > 3)
                df['wind_chill_f'] = np.nan

                # Wind chill formula
                df.loc[mask, 'wind_chill_f'] = 35.74 + \
                                              0.6215 * df.loc[mask, 'temperature_f'] - \
                                              35.75 * wind_speed_mph.loc[mask] ** 0.16 + \
                                              0.4275 * df.loc[mask, 'temperature_f'] * wind_speed_mph.loc[mask] ** 0.16

                # Convert to Celsius
                df['wind_chill'] = (df['wind_chill_f'] - 32) * 5/9

            # Calculate weather condition changes
            if 'weather_main' in df.columns:
                df['weather_changed'] = df['weather_main'] != df['weather_main'].shift(1)

            # Calculate rainfall metrics if available
            if 'rain_1h' in df.columns:
                # Fill NaN values with 0
                df['rain_1h'] = df['rain_1h'].fillna(0)

                # Calculate cumulative rainfall
                df['rain_cumulative_24h'] = df['rain_1h'].rolling(window=24).sum()  # Assuming hourly data

            # Identify extreme weather conditions
            if 'temperature' in df.columns:
                df['extreme_hot'] = df['temperature'] > 35  # > 95°F
                df['extreme_cold'] = df['temperature'] < -5  # < 23°F

            if 'wind_speed' in df.columns:
                df['high_wind'] = df['wind_speed'] > 10.7  # > 24 mph (strong breeze)

            if 'humidity' in df.columns:
                df['extreme_dry'] = df['humidity'] < 20
                df['extreme_humid'] = df['humidity'] > 90

            # Log processing details
            logger.info(f"Processed {len(df)} current weather records")
            logger.debug(f"Current weather data columns: {df.columns.tolist()}")

            return df

        except Exception as e:
            logger.error(f"Error processing current weather data: {e}")
            return pd.DataFrame()

    def process_forecast_data(self, data_list):
        """
        Process a list of forecast weather data entries.

        Args:
            data_list (list): List of dictionaries containing forecast data

        Returns:
            pandas.DataFrame: Processed data as a DataFrame
        """
        if not data_list:
            logger.warning("No forecast data to process")
            return pd.DataFrame()

        try:
            # Convert to DataFrame
            df = pd.DataFrame(data_list)

            # Convert timestamps to datetime if they're not already
            for col in ['collection_timestamp', 'forecast_timestamp']:
                if col in df.columns and not pd.api.types.is_datetime64_dtype(df[col]):
                    df[col] = pd.to_datetime(df[col])

            # Sort by forecast timestamp
            df.sort_values('forecast_timestamp', inplace=True)

            # Group by collection timestamp to get the most recent forecast for each time period
            latest_collection = df['collection_timestamp'].max()
            latest_forecasts = df[df['collection_timestamp'] == latest_collection]

            # Calculate time until forecast (from collection time)
            latest_forecasts['hours_until_forecast'] = (latest_forecasts['forecast_timestamp'] - latest_collection).dt.total_seconds() / 3600

            # Convert temperature to Fahrenheit if needed
            if 'temperature' in latest_forecasts.columns and 'temperature_f' not in latest_forecasts.columns:
                latest_forecasts['temperature_f'] = latest_forecasts['temperature'] * 9/5 + 32

            # Calculate daily min/max temperatures
            if 'temperature' in latest_forecasts.columns:
                latest_forecasts['forecast_date'] = latest_forecasts['forecast_timestamp'].dt.date
                daily_stats = latest_forecasts.groupby('forecast_date').agg({
                    'temperature': ['min', 'max', 'mean'],
                    'humidity': ['min', 'max', 'mean'],
                    'pop': ['max', 'mean']  # Probability of precipitation
                })

                # Flatten MultiIndex columns
                daily_stats.columns = ['_'.join(col).strip() for col in daily_stats.columns.values]
                daily_stats.reset_index(inplace=True)

                # Convert back to DataFrame with datetime index
                daily_stats['forecast_date'] = pd.to_datetime(daily_stats['forecast_date'])

            # Log processing details
            logger.info(f"Processed {len(latest_forecasts)} forecast records from {latest_collection}")
            logger.debug(f"Forecast data columns: {latest_forecasts.columns.tolist()}")

            return latest_forecasts

        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return pd.DataFrame()

    def calculate_forecast_accuracy(self, forecasts_df, actuals_df):
        """
        Calculate accuracy of previous forecasts compared to actual measurements.

        Args:
            forecasts_df (pandas.DataFrame): Historical forecast data
            actuals_df (pandas.DataFrame): Actual weather measurements

        Returns:
            pandas.DataFrame: Accuracy metrics
        """
        if forecasts_df.empty or actuals_df.empty:
            logger.warning("Cannot calculate forecast accuracy: missing data")
            return pd.DataFrame()

        try:
            # Prepare timestamps for joining
            forecasts_df = forecasts_df.copy()
            actuals_df = actuals_df.copy()

            # Ensure timestamps are datetime
            forecasts_df['forecast_timestamp'] = pd.to_datetime(forecasts_df['forecast_timestamp'])
            actuals_df['timestamp'] = pd.to_datetime(actuals_df['timestamp'])

            # Round timestamps to nearest hour to facilitate joining
            forecasts_df['forecast_hour'] = forecasts_df['forecast_timestamp'].dt.floor('H')
            actuals_df['actual_hour'] = actuals_df['timestamp'].dt.floor('H')

            # Join forecasts with actuals
            merged = pd.merge(
                forecasts_df,
                actuals_df,
                left_on='forecast_hour',
                right_on='actual_hour',
                suffixes=('_forecast', '_actual')
            )

            # Calculate error metrics
            if not merged.empty:
                merged['temp_error'] = merged['temperature_forecast'] - merged['temperature_actual']
                merged['temp_abs_error'] = abs(merged['temp_error'])
                merged['humidity_error'] = merged['humidity_forecast'] - merged['humidity_actual']
                merged['humidity_abs_error'] = abs(merged['humidity_error'])

                # Calculate percentage error
                merged['temp_pct_error'] = (merged['temp_error'] / merged['temperature_actual']) * 100
                merged['humidity_pct_error'] = (merged['humidity_error'] / merged['humidity_actual']) * 100

                # Group by forecast lead time (hours from collection to forecast)
                merged['lead_time'] = (merged['forecast_timestamp'] - merged['collection_timestamp']).dt.total_seconds() / 3600
                merged['lead_time_bin'] = pd.cut(merged['lead_time'],
                                               bins=[0, 24, 48, 72, 96, 120],
                                               labels=['24h', '48h', '72h', '96h', '120h'])

                accuracy_by_leadtime = merged.groupby('lead_time_bin').agg({
                    'temp_abs_error': ['mean', 'median', 'std'],
                    'temp_pct_error': ['mean', 'median', 'std'],
                    'humidity_abs_error': ['mean', 'median', 'std'],
                    'humidity_pct_error': ['mean', 'median', 'std']
                })

                # Flatten MultiIndex columns
                accuracy_by_leadtime.columns = ['_'.join(col).strip() for col in accuracy_by_leadtime.columns.values]
                accuracy_by_leadtime.reset_index(inplace=True)

                logger.info(f"Calculated forecast accuracy for {len(merged)} matched records")
                return accuracy_by_leadtime
            else:
                logger.warning("No matching records found for forecast accuracy calculation")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error calculating forecast accuracy: {e}")
            return pd.DataFrame()

    def detect_anomalies(self, df, column, window=24, threshold=2.0):
        """
        Detect anomalies in time series data using a rolling Z-score method.

        Args:
            df (pandas.DataFrame): Weather data
            column (str): Column name to analyze for anomalies
            window (int): Rolling window size for baseline
            threshold (float): Z-score threshold for anomaly detection

        Returns:
            pandas.DataFrame: Original DataFrame with anomaly flags added
        """
        if df.empty or column not in df.columns:
            logger.warning(f"Cannot detect anomalies: missing data or column '{column}'")
            return df

        try:
            # Make a copy to avoid modifying the original
            result_df = df.copy()

            # Calculate rolling mean and standard deviation
            rolling_mean = result_df[column].rolling(window=window).mean()
            rolling_std = result_df[column].rolling(window=window).std()

            # Calculate Z-scores
            result_df[f'{column}_zscore'] = (result_df[column] - rolling_mean) / rolling_std

            # Flag anomalies
            result_df[f'{column}_anomaly'] = abs(result_df[f'{column}_zscore']) > threshold

            # Log anomaly detection results
            anomaly_count = result_df[f'{column}_anomaly'].sum()
            logger.info(f"Detected {anomaly_count} anomalies in '{column}' using Z-score threshold {threshold}")

            return result_df

        except Exception as e:
            logger.error(f"Error detecting anomalies in {column}: {e}")
            return df

    def generate_daily_report(self, current_df, forecast_df):
        """
        Generate a daily report with key weather metrics and forecasts.

        Args:
            current_df (pandas.DataFrame): Current weather data
            forecast_df (pandas.DataFrame): Forecast data

        Returns:
            dict: Report data with summary statistics and forecasts
        """
        if current_df.empty and forecast_df.empty:
            logger.warning("Cannot generate report: missing data")
            return {}

        try:
            report = {
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'current': {},
                'forecast': {},
                'trends': {}
            }

            # Current weather summary
            if not current_df.empty:
                # Get most recent record
                latest = current_df.iloc[-1]

                report['current'] = {
                    'temperature': float(latest.get('temperature', 'N/A')),
                    'feels_like': float(latest.get('feels_like', 'N/A')),
                    'humidity': float(latest.get('humidity', 'N/A')),
                    'weather_main': latest.get('weather_main', 'N/A'),
                    'weather_description': latest.get('weather_description', 'N/A'),
                    'wind_speed': float(latest.get('wind_speed', 'N/A')),
                    'wind_direction': float(latest.get('wind_direction', 'N/A')),
                    'pressure': float(latest.get('pressure', 'N/A')),
                    'timestamp': latest.get('timestamp', datetime.now()).isoformat()
                }

                # Get 24-hour statistics
                last_24h = current_df[current_df['timestamp'] >= (latest['timestamp'] - timedelta(hours=24))]
                if not last_24h.empty:
                    report['trends']['last_24h'] = {
                        'temp_min': float(last_24h['temperature'].min()),
                        'temp_max': float(last_24h['temperature'].max()),
                        'temp_avg': float(last_24h['temperature'].mean()),
                        'humidity_avg': float(last_24h['humidity'].mean()),
                        'conditions': last_24h['weather_main'].value_counts().index[0]
                    }

            # Forecast summary
            if not forecast_df.empty:
                # Group forecasts by day
                forecast_df['forecast_date'] = forecast_df['forecast_timestamp'].dt.date
                daily_forecasts = forecast_df.groupby('forecast_date').agg({
                    'temperature': ['min', 'max', 'mean'],
                    'humidity': ['mean'],
                    'pop': ['max'],
                    'weather_main': lambda x: x.value_counts().index[0]
                })

                # Flatten column names
                daily_forecasts.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in daily_forecasts.columns]

                # Add to report
                report['forecast']['daily'] = {}
                for date, row in daily_forecasts.iterrows():
                    report['forecast']['daily'][date.isoformat()] = {
                        'temp_min': float(row['temperature_min']),
                        'temp_max': float(row['temperature_max']),
                        'temp_avg': float(row['temperature_mean']),
                        'humidity': float(row['humidity_mean']),
                        'precipitation_chance': float(row['pop_max'] * 100) if not pd.isna(row['pop_max']) else 0,
                        'conditions': row['weather_main']
                    }

            logger.info(f"Generated daily weather report for {report['report_date']}")
            return report

        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
            return {'error': str(e)}
