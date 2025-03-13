# Weather ETL and AI Chatbot Project Specification

## Project Overview

This project implements a nightly ETL pipeline to collect and store weather data for Louisville, KY in a PostgreSQL database, with an AI-powered chatbot interface that allows users to query this data using natural language. The system will support complex analytical capabilities through text-to-SQL conversion.

## Technical Stack

- **ETL Orchestration**: Apache Airflow
- **Programming Language**: Python 3.x
- **Database**: PostgreSQL
- **Data Processing**: Pandas
- **AI Component**: OpenAI API (GPT-4o-mini)
- **Hosting**: Local development environment (macOS)
- **Future Consideration**: Migration to Databricks

## Database Schema

### 1. locations Table

```sql
CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    population INTEGER,
    timezone VARCHAR(50)
);
```

### 2. weather_data Table

```sql
CREATE TABLE weather_data (
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
    clouds_percentage INTEGER
);
```

## ETL Pipeline

### Data Source

- OpenWeatherMap API
  - Current weather data endpoint
  - Historical weather data endpoint (if needed)
  - API key will need to be configured

### ETL Process

1. **Extract**:

   - Fetch daily weather data for Louisville, KY from OpenWeatherMap API
   - Store raw response as backup

2. **Transform**:

   - Parse JSON response into structured format
   - Clean and validate data (handle missing values, convert units if needed)
   - Structure data according to database schema

3. **Load**:
   - Upsert data into PostgreSQL database
   - For the locations table: Insert only if location doesn't exist
   - For the weather_data table: Replace existing data to maintain only latest records

### Airflow DAG Configuration

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_etl_pipeline',
    default_args=default_args,
    description='A DAG to fetch and load weather data',
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

extract_task = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_weather_data',
    python_callable=transform_weather_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_weather_data',
    python_callable=load_weather_data,
    dag=dag,
)

extract_task >> transform_task >> load_task
```

## Error Handling Strategy

- Implement try-except blocks in all API calls and database operations
- Log critical errors to a dedicated error log
- If API call fails, use most recent valid data from the database
- Implement Airflow task retries (3 attempts with 5-minute intervals)
- Send notification on critical failures (implement in future iteration)

## Monitoring Plan

- Log all critical errors with timestamps and error details
- Create a simple dashboard in Airflow to monitor DAG execution status
- Track API response times and database operation durations
- Monitor disk space usage for database growth

## AI Chatbot Implementation

### Architecture

- Flask web application for chatbot interface
- OpenAI API integration for text-to-SQL conversion
- PostgreSQL connector for executing generated queries

### Text-to-SQL Approach

- Implement agent-based approach using OpenAI's function calling
- Provide database schema as context to the model
- Validate generated SQL before execution
- Implement iterative refinement for failed queries

### Chatbot Features

1. Support for casual conversational queries about weather
2. Complex analytical capabilities:
   - Historical trend analysis
   - Correlation between weather metrics
   - Anomaly detection
   - Seasonal comparisons
   - Visualization generation
   - Simple forecasting
   - Comparative analysis

### Sample Prompt Structure

```python
def generate_sql_query(user_question):
    schema_info = """
    Table: locations
    Columns: location_id, city_name, country, latitude, longitude, population, timezone

    Table: weather_data
    Columns: weather_id, location_id, timestamp, temperature, feels_like, humidity,
             pressure, wind_speed, wind_direction, weather_condition,
             weather_description, precipitation, visibility, clouds_percentage

    Relationships: weather_data.location_id is a foreign key to locations.location_id
    """

    system_prompt = f"""
    You are an AI assistant that converts natural language questions about weather data
    into SQL queries. Use the following database schema:

    {schema_info}

    Generate a valid PostgreSQL query that answers the user's question.
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        functions=[{
            "name": "execute_sql_query",
            "description": "Execute a SQL query against the weather database",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        }],
        function_call={"name": "execute_sql_query"}
    )

    return response.choices[0].message.function_call.arguments["sql"]
```

## Testing Plan

### ETL Testing

1. **Unit Tests**:

   - Test API connection and data extraction
   - Test data transformation functions
   - Test database connection and loading

2. **Integration Tests**:

   - Test complete ETL pipeline with sample API responses
   - Verify data integrity in database

3. **Error Handling Tests**:
   - Test behavior when API is unavailable
   - Test behavior with malformed API responses
   - Test behavior with database connection issues

### Chatbot Testing

1. **Query Generation Tests**:

   - Test text-to-SQL conversion with various question types
   - Verify SQL correctness and execution

2. **Conversation Flow Tests**:

   - Test handling of follow-up questions
   - Test conversational context maintenance

3. **Edge Case Tests**:
   - Test handling of ambiguous questions
   - Test handling of queries outside data scope

## Implementation Plan

1. **Phase 1**: Setup development environment

   - Install PostgreSQL, Python, Airflow
   - Configure database schema
   - Set up API access

2. **Phase 2**: Implement ETL pipeline

   - Develop extraction scripts
   - Implement transformation logic
   - Create loading procedures
   - Configure Airflow DAG

3. **Phase 3**: Implement chatbot

   - Set up OpenAI API integration
   - Develop text-to-SQL conversion
   - Create chatbot interface
   - Implement visualization capabilities

4. **Phase 4**: Testing and refinement
   - Execute testing plan
   - Refine based on test results
   - Document system behavior

## Future Enhancements

- Add user authentication
- Expand to multiple locations
- Implement data archiving for historical analysis
- Migrate to Databricks for improved scalability
- Add more complex analytical capabilities

This specification provides a complete roadmap for implementing a weather data ETL pipeline with an AI chatbot interface, focusing on Louisville, KY weather data. The implementation follows industry best practices and leverages modern technologies to create a robust, maintainable system.
