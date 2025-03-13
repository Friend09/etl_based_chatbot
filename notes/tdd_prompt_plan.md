# Weather ETL and AI Chatbot Implementation Blueprint

After analyzing the provided specification, I'll develop a detailed plan broken down into small, manageable steps that build iteratively. Each step will include a code-generation prompt designed for test-driven implementation.

## Project Overview

This project involves building:

1. A nightly ETL pipeline that collects weather data from OpenWeatherMap API
2. Storage in PostgreSQL database
3. Apache Airflow for orchestration
4. An AI-powered chatbot using OpenAI's GPT-4o-mini for natural language queries
5. A Flask web application as the frontend

## Implementation Blueprint

I'll organize the implementation into logical chunks, with each chunk broken down into specific steps. Each step will have a corresponding prompt for a code-generation LLM.

### Chunk 1: Project Setup and Basic Infrastructure

#### Step 1.1: Project Structure and Environment Setup

```markdown
# Prompt: Project Structure and Environment Setup

Create a well-organized project structure for a weather ETL and AI chatbot application. The application will collect weather data for Louisville, KY using OpenWeatherMap API, store it in PostgreSQL, and provide a natural language interface using OpenAI's GPT-4o-mini.

Follow these requirements:

1. Create a main project directory named "weather_etl_chatbot"
2. Set up subdirectories for different components:
   - etl/ (for ETL pipeline code)
   - web/ (for Flask application)
   - database/ (for database utilities and scripts)
   - config/ (for configuration files)
   - tests/ (for test cases)
3. Create a Python virtual environment setup
4. Generate a requirements.txt with these dependencies:
   - psycopg2-binary
   - pandas
   - requests
   - python-dotenv
   - Flask
   - openai
   - apache-airflow
   - pytest
5. Create a .gitignore file with appropriate patterns
6. Add a README.md with project description
7. Create a setup.py file for the project

Include appropriate documentation in each file. Use best practices for Python project structure.
```

#### Step 1.2: Configuration Management

```markdown
# Prompt: Configuration Management

Create a robust configuration management system for the weather ETL and chatbot application. The system should handle different environments (development, testing, production) and manage sensitive information securely.

Requirements:

1. Create a config module with:

   - Environment variable loading using python-dotenv
   - Configuration validation
   - Default configuration values
   - Support for different environments

2. Implement these configuration categories:

   - Database (PostgreSQL connection parameters)
   - API keys (OpenWeatherMap, OpenAI)
   - Airflow settings
   - Application settings (Flask)

3. Create a template .env file with placeholders for all required variables

4. Implement a configuration validation function that checks all required settings are present

5. Write unit tests for the configuration module that verify:
   - Configuration loading works correctly
   - Validation identifies missing required settings
   - Environment-specific settings are applied correctly

Use best practices for secure configuration management in Python applications.
```

#### Step 1.3: Logging Setup

```markdown
# Prompt: Logging Setup

Implement a comprehensive logging system for the weather ETL and chatbot application. The system should provide detailed logs for debugging while keeping sensitive information secure.

Requirements:

1. Create a logging module that:

   - Configures Python's built-in logging library
   - Supports different log levels based on environment
   - Provides both file and console handlers
   - Includes contextual information in logs (timestamps, module, function)
   - Masks sensitive information (API keys, credentials)

2. Implement these logging components:

   - A base Logger class or function
   - Specialized loggers for ETL, web app, and database components
   - Log rotation configuration for production

3. Create utility functions for:

   - Accessing logger instances
   - Setting log levels dynamically
   - Formatting structured logs (for potential integration with log aggregation)

4. Write unit tests that verify:
   - Logs are properly formatted
   - Sensitive information is masked
   - Different components log to appropriate destinations

Use best practices for logging in Python applications.
```

#### Step 1.4: Database Schema and Utilities

```markdown
# Prompt: Database Schema and Utilities

Create the database schema and utility functions for the weather ETL and chatbot application. The system needs to store location and weather data efficiently and provide clean interfaces for database operations.

Requirements:

1. Create SQL scripts to:

   - Initialize the database
   - Create the locations table as defined in the spec
   - Create the weather_data table as defined in the spec
   - Set up appropriate indexes for efficient querying

2. Implement a database utility module with functions for:

   - Establishing and managing database connections (including connection pooling)
   - Executing queries safely (parameterized queries)
   - Transaction management
   - Error handling

3. Create helper functions for common database operations:

   - Checking if location exists
   - Upserting weather data
   - Querying weather data with various filters

4. Write unit tests that verify:
   - Database connection works correctly
   - Tables are created with proper constraints
   - Basic CRUD operations function as expected
   - Error conditions are handled gracefully

Use best practices for database operations in Python, including preventing SQL injection and proper resource management.
```

### Chunk 2: Basic ETL Components

#### Step 2.1: OpenWeatherMap API Client

```markdown
# Prompt: OpenWeatherMap API Client

Implement a robust API client for OpenWeatherMap that will be used in the weather ETL pipeline. The client should handle API interactions, error conditions, and provide a clean interface for the ETL process.

Requirements:

1. Create an OpenWeatherMapClient class that:

   - Takes API key from configuration
   - Provides methods to fetch current weather data
   - Handles error conditions (HTTP errors, rate limits, timeouts)
   - Includes retry logic for transient failures
   - Implements proper logging

2. Implement these specific methods:

   - get_current_weather(city_name, country_code)
   - get_weather_by_coordinates(latitude, longitude)
   - get_weather_forecast(city_name, country_code, days=5)

3. Include helper methods for:

   - Parsing API responses
   - Validating API responses
   - Converting units if needed (e.g., Kelvin to Celsius)

4. Write unit tests that:
   - Test successful API interactions (using mocks)
   - Verify error handling works correctly
   - Test parsing of sample responses
   - Check retry logic functions as expected

Use best practices for API clients in Python, including proper error handling, logging, and resource management.
```

#### Step 2.2: Data Extraction Module

```markdown
# Prompt: Data Extraction Module

Create the data extraction module for the weather ETL pipeline. This module will use the OpenWeatherMap client to fetch weather data and prepare it for transformation.

Requirements:

1. Implement an extraction module that:

   - Uses the OpenWeatherMap client to fetch data
   - Handles extraction for a specific location (Louisville, KY)
   - Includes error handling and logging
   - Saves raw responses as backup

2. Create these specific components:

   - An Extractor class that orchestrates the extraction process
   - A function to validate extraction results
   - Error handling for failed extractions
   - Retry logic for transient failures

3. Implement features for:

   - Saving raw API responses to disk
   - Maintaining extraction metadata (timestamps, status)
   - Logging extraction metrics (duration, size)

4. Write unit tests that verify:
   - Data extraction works correctly
   - Failed extractions are handled properly
   - Backups are created as expected
   - Extraction metrics are accurate

Use best practices for ETL extraction in Python, including proper error handling, backups, and validation.
```

#### Step 2.3: Data Transformation Module

```markdown
# Prompt: Data Transformation Module

Implement the data transformation module for the weather ETL pipeline. This module will convert raw API responses into structured data ready for loading into the database.

Requirements:

1. Create a transformation module that:

   - Parses JSON responses from the extraction step
   - Cleans and validates the data
   - Structures data according to the database schema
   - Handles missing or invalid values

2. Implement these transformation functions:

   - transform_location_data(raw_data) -> location_dict
   - transform_weather_data(raw_data) -> weather_dict
   - validate_transformed_data(transformed_data) -> boolean

3. Include data cleaning utilities for:

   - Converting units (if needed)
   - Handling missing values
   - Normalizing text fields (e.g., weather conditions)
   - Validating data types and ranges

4. Write unit tests that verify:
   - Transformation produces correctly structured data
   - Data validation catches invalid values
   - Missing values are handled appropriately
   - Edge cases are properly managed

Use best practices for ETL transformation in Python, focusing on data quality, validation, and proper error handling.
```

#### Step 2.4: Data Loading Module

```markdown
# Prompt: Data Loading Module

Create the data loading module for the weather ETL pipeline. This module will insert transformed data into the PostgreSQL database, handling updates and maintaining data integrity.

Requirements:

1. Implement a loading module that:

   - Takes transformed data from the transformation step
   - Handles database connections securely
   - Implements upsert logic for both tables
   - Maintains data integrity with transactions

2. Create these specific functions:

   - upsert_location(location_data) -> location_id
   - upsert_weather_data(weather_data, location_id) -> weather_id
   - verify_loaded_data(data_dict, table_name) -> boolean

3. Include error handling for:

   - Database connection issues
   - Constraint violations
   - Transaction failures
   - Deadlocks or concurrent access issues

4. Write unit tests that verify:
   - Data is correctly loaded into the database
   - Upsert logic works for both insert and update cases
   - Transactions maintain data integrity
   - Error conditions are handled gracefully

Use best practices for ETL loading in Python, including parameterized queries to prevent SQL injection, proper transaction management, and error handling.
```

#### Step 2.5: ETL Integration Test

```markdown
# Prompt: ETL Integration Test

Create comprehensive integration tests for the ETL pipeline components developed so far. These tests should verify that the extraction, transformation, and loading modules work together correctly.

Requirements:

1. Implement integration tests that:

   - Test the complete flow from extraction to loading
   - Use mock API responses for reproducibility
   - Set up and tear down test database state
   - Verify data integrity throughout the pipeline

2. Create test fixtures for:

   - Sample API responses (both valid and invalid)
   - Database setup and teardown
   - Configuration for testing environment

3. Test these specific scenarios:

   - Successful ETL flow with valid data
   - Handling of API errors during extraction
   - Recovery from transformation errors
   - Database errors during loading
   - End-to-end validation of data integrity

4. Implement helper functions for test validation:
   - Comparing loaded data with expected results
   - Verifying database state after loading
   - Checking log output for expected messages

Use best practices for testing ETL pipelines, including proper isolation, reproducibility, and comprehensive validation.
```

### Chunk 3: Airflow Integration

#### Step 3.1: Airflow Setup and Configuration

```markdown
# Prompt: Airflow Setup and Configuration

Set up and configure Apache Airflow for the weather ETL pipeline. This will handle scheduling and monitoring of the ETL process.

Requirements:

1. Create scripts and instructions for:

   - Installing Airflow in the project environment
   - Configuring Airflow for local development
   - Setting up the Airflow database
   - Configuring Airflow home directory

2. Implement Airflow configuration for:

   - Database connection
   - Email notifications (if applicable)
   - Executor configuration (LocalExecutor for development)
   - Logging settings

3. Create a utility module for Airflow that:

   - Provides common functions used across DAGs
   - Handles configuration loading
   - Sets up connections to external systems
   - Configures default arguments

4. Write tests that verify:
   - Airflow installation is correct
   - Configuration is loaded properly
   - Connections to external systems work

Use best practices for Airflow setup and configuration, focusing on reproducibility and proper separation of concerns.
```

#### Step 3.2: ETL DAG Implementation

```markdown
# Prompt: ETL DAG Implementation

Create an Apache Airflow DAG (Directed Acyclic Graph) for the weather ETL pipeline. This DAG will orchestrate the extraction, transformation, and loading process on a daily schedule.

Requirements:

1. Create a DAG file that:

   - Uses the schedule defined in the spec (@daily)
   - Has appropriate default arguments
   - Sets up task dependencies correctly
   - Includes proper documentation

2. Implement these operators:

   - PythonOperator for extract_weather_data
   - PythonOperator for transform_weather_data
   - PythonOperator for load_weather_data

3. Add these DAG features:

   - Retries for failed tasks (3 attempts with 5-minute intervals)
   - Task timeout configuration
   - Appropriate task dependencies (extract >> transform >> load)
   - Logging of task execution

4. Write tests that verify:
   - DAG structure is correct
   - Operators are configured properly
   - Task dependencies are set correctly
   - Default arguments are applied

Use best practices for Airflow DAG development, including proper documentation, error handling, and configuration.
```

#### Step 3.3: Airflow Operators and Task Functions

```markdown
# Prompt: Airflow Operators and Task Functions

Implement the task functions and operators for the Airflow DAG that will execute the weather ETL pipeline. These functions will integrate with the extraction, transformation, and loading modules developed earlier.

Requirements:

1. Create task functions for:

   - extract_weather_data()
   - transform_weather_data()
   - load_weather_data()

2. Implement proper interactions with:

   - The ETL modules from previous steps
   - Airflow context variables
   - XComs for sharing data between tasks

3. Add these features to task functions:

   - Comprehensive error handling
   - Logging of task progress
   - Performance metrics (duration, data size)
   - Status reporting

4. Write tests that verify:
   - Task functions execute correctly
   - Error handling works as expected
   - XComs are properly used for data sharing
   - Tasks integrate with ETL modules correctly

Use best practices for Airflow task implementation, including proper error handling, logging, and resource management.
```

#### Step 3.4: Error Handling and Monitoring

```markdown
# Prompt: Error Handling and Monitoring for Airflow

Enhance the Airflow implementation with robust error handling and monitoring capabilities. This will ensure the ETL pipeline is reliable and issues are promptly detected.

Requirements:

1. Implement error handling mechanisms:

   - Custom exceptions for different error types
   - Try-except blocks in all task functions
   - Proper error reporting and logging
   - Fallback strategies for common failures

2. Create monitoring components:

   - Airflow sensors to monitor external dependencies
   - Custom callbacks for task events
   - Metrics collection for task duration and status
   - Alerting configuration for critical failures

3. Add these specific features:

   - SLA monitoring for tasks
   - Email notifications for failures
   - Logging of detailed error information
   - Recovery mechanisms for specific error types

4. Write tests that verify:
   - Error handling correctly manages different failure scenarios
   - Monitoring components detect issues correctly
   - Alerts are generated for appropriate conditions
   - Recovery mechanisms work as expected

Use best practices for Airflow monitoring and error handling, focusing on reliability, observability, and fault tolerance.
```

### Chunk 4: Flask Web Application

#### Step 4.1: Flask Application Setup

```markdown
# Prompt: Flask Application Setup

Create the basic structure for the Flask web application that will serve as the frontend for the weather chatbot. This application will provide a user interface for interacting with the AI chatbot.

Requirements:

1. Implement a Flask application with:

   - Proper application factory pattern
   - Configuration loading from the project config
   - Basic error handling and logging
   - Blueprint structure for modularity

2. Create these routes:

   - / (index) - Landing page
   - /chat - Chatbot interface
   - /health - Health check endpoint
   - /api/message - API endpoint for chat messages

3. Set up the application structure with:

   - Templates directory with base template
   - Static files directory for CSS, JavaScript, and images
   - Error templates
   - Configuration handling

4. Write tests that verify:
   - Application initializes correctly
   - Routes return expected responses
   - Error handling works as expected
   - Configuration is loaded properly

Use best practices for Flask application development, including the application factory pattern, blueprints, and proper resource management.
```

#### Step 4.2: Database Integration for Flask

```markdown
# Prompt: Database Integration for Flask

Implement database integration for the Flask web application. This will allow the application to query the weather database and serve data to the chatbot interface.

Requirements:

1. Create a database module for Flask that:

   - Manages database connections efficiently
   - Provides a clean API for querying data
   - Handles errors gracefully
   - Implements connection pooling for performance

2. Implement these specific functions:

   - get_db_connection() -> connection
   - execute_query(query, params) -> results
   - get_weather_data(location_id, start_date, end_date) -> data
   - get_location_by_name(city_name) -> location

3. Add these features:

   - Connection pooling with appropriate sizing
   - Transaction management
   - Query parameterization for security
   - Result formatting for JSON responses

4. Write tests that verify:
   - Database connections work correctly
   - Queries return expected results
   - Error handling works properly
   - Connection pooling functions correctly

Use best practices for database integration in Flask applications, including proper resource management, security considerations, and error handling.
```

#### Step 4.3: Chat Interface - Frontend

```markdown
# Prompt: Chat Interface Frontend

Create the frontend for the chatbot interface. This will provide a user-friendly way for users to interact with the weather chatbot.

Requirements:

1. Implement HTML templates for:

   - Base template with common structure
   - Chat interface with message history and input
   - Error pages with user-friendly messages

2. Create CSS styles for:

   - Responsive layout that works on different devices
   - Chat bubbles for user and bot messages
   - Loading indicators and animations
   - Overall visual design consistent with a weather theme

3. Implement JavaScript for:

   - Handling user input and form submission
   - Sending AJAX requests to the chat API
   - Updating the chat history dynamically
   - Managing the chat state and history

4. Add features for:
   - Displaying different message types (text, charts, errors)
   - Handling long responses appropriately
   - Providing feedback during processing
   - Mobile-friendly interaction

Test the interface in different browsers and screen sizes to ensure compatibility and responsiveness.
```

#### Step 4.4: Chat API Endpoint

```markdown
# Prompt: Chat API Endpoint

Implement the API endpoint for the chatbot that will receive user messages and return responses. This endpoint will serve as the bridge between the frontend and the AI chatbot logic.

Requirements:

1. Create a Flask route for /api/message that:

   - Accepts POST requests with JSON data
   - Validates input data
   - Returns JSON responses
   - Handles errors appropriately

2. Implement these features:

   - Request validation and sanitization
   - CSRF protection
   - Rate limiting for API requests
   - Response formatting

3. Add these specific functions:

   - validate_message_request(request_data) -> bool
   - format_chatbot_response(response) -> json
   - log_chat_interaction(user_message, bot_response)

4. Write tests that verify:
   - Endpoint correctly handles valid requests
   - Validation rejects invalid requests
   - Rate limiting works as expected
   - Responses are properly formatted

Use best practices for API development in Flask, including proper validation, security considerations, and error handling.
```

### Chunk 5: OpenAI Integration for Text-to-SQL

#### Step 5.1: OpenAI Client Integration

```markdown
# Prompt: OpenAI Client Integration

Implement the OpenAI client integration for the weather chatbot. This client will handle communication with the OpenAI API to generate SQL queries from natural language.

Requirements:

1. Create an OpenAI client module that:

   - Manages API key securely
   - Handles API requests and responses
   - Implements error handling and retries
   - Provides logging for API interactions

2. Implement these specific functions:

   - initialize_openai_client() -> client
   - generate_completion(prompt, options) -> response
   - parse_openai_response(response) -> structured_data
   - handle_api_error(error) -> fallback_response

3. Add these features:

   - Rate limiting compliance
   - Timeout handling
   - Response validation
   - Cost tracking (token usage)

4. Write tests that verify:
   - Client initialization works correctly
   - API requests are formatted properly
   - Responses are parsed correctly
   - Error handling works as expected

Use best practices for AI API integration, including proper error handling, security considerations, and resource management.
```

#### Step 5.2: Text-to-SQL Conversion

```markdown
# Prompt: Text-to-SQL Conversion

Implement the text-to-SQL conversion system using OpenAI's API. This system will convert natural language questions into SQL queries that can be executed against the weather database.

Requirements:

1. Create a text-to-SQL module that:

   - Takes natural language input
   - Generates appropriate SQL using OpenAI
   - Validates and sanitizes generated SQL
   - Handles edge cases and errors

2. Implement these specific functions:

   - generate_sql_query(user_question) -> sql_query
   - validate_sql_query(sql_query) -> (is_valid, error_message)
   - get_schema_context() -> schema_string
   - format_system_prompt(schema) -> prompt

3. Add these features:

   - Context management for multi-turn conversations
   - Integration with database schema information
   - Query templates for common questions
   - Fallback mechanisms for failed conversions

4. Write tests that verify:
   - Conversion works for different question types
   - Generated SQL is valid and safe
   - Edge cases are handled correctly
   - Context management works as expected

Use best practices for prompt engineering and SQL generation, including proper validation, security considerations, and error handling.
```

#### Step 5.3: SQL Validation and Execution

```markdown
# Prompt: SQL Validation and Execution

Create a system to validate and safely execute SQL queries generated from natural language. This system will ensure that queries are safe, efficient, and produce useful results.

Requirements:

1. Implement a SQL validation and execution module that:

   - Validates SQL syntax and structure
   - Checks for unsafe operations
   - Executes queries safely
   - Formats results for display

2. Create these specific functions:

   - validate_sql_safety(sql_query) -> (is_safe, reason)
   - execute_validated_query(sql_query) -> results
   - format_query_results(results) -> formatted_results
   - handle_query_error(error) -> user_friendly_message

3. Add these safety features:

   - Query whitelisting (SELECT only)
   - Table and column validation
   - Query complexity limits
   - Execution timeout

4. Write tests that verify:
   - Validation correctly identifies unsafe queries
   - Execution returns expected results
   - Results are formatted correctly
   - Errors are handled gracefully

Use best practices for SQL security, including prevention of SQL injection, proper validation, and safe execution.
```

#### Step 5.4: Query Result Formatting and Explanation

```markdown
# Prompt: Query Result Formatting and Explanation

Implement a system to format query results and generate natural language explanations of the data. This will make the chatbot's responses more user-friendly and informative.

Requirements:

1. Create a result formatting and explanation module that:

   - Takes query results and formats them appropriately
   - Generates natural language summaries of results
   - Identifies key insights in the data
   - Handles different result types

2. Implement these specific functions:

   - format_table_results(results) -> formatted_html
   - generate_result_summary(results) -> summary_text
   - identify_key_insights(results) -> insights_list
   - format_empty_results(query) -> friendly_message

3. Add these features:

   - Tabular formatting for structured data
   - Statistical summaries (avg, min, max, etc.)
   - Trend identification
   - Handling of null/empty results

4. Write tests that verify:
   - Formatting works for different result types
   - Summaries accurately describe the data
   - Insights are meaningful and relevant
   - Empty results are handled gracefully

Use best practices for data presentation and natural language generation, focusing on clarity, accuracy, and user experience.
```

### Chunk 6: Chatbot Core Logic

#### Step 6.1: Chatbot Message Processing

```markdown
# Prompt: Chatbot Message Processing

Implement the core message processing logic for the weather chatbot. This system will handle user messages, maintain conversation context, and coordinate the various components of the chatbot.

Requirements:

1. Create a chatbot processor that:

   - Takes user messages as input
   - Maintains conversation history
   - Determines appropriate handling for each message
   - Returns structured responses

2. Implement these specific functions:

   - process_message(user_message, conversation_id) -> response
   - update_conversation_history(conversation_id, message, response)
   - determine_message_intent(message, history) -> intent
   - format_chatbot_response(response_data) -> formatted_response

3. Add these features:

   - Session management for conversations
   - Context preservation between messages
   - Intent detection for different query types
   - Fallback handling for unclear messages

4. Write tests that verify:
   - Processing works for different message types
   - Conversation history is maintained correctly
   - Intent detection works as expected
   - Responses are formatted correctly

Use best practices for chatbot development, including proper state management, context handling, and response generation.
```

#### Step 6.2: Conversation State Management

```markdown
# Prompt: Conversation State Management

Create a system to manage conversation state for the weather chatbot. This will allow the chatbot to maintain context across multiple messages and provide more coherent responses.

Requirements:

1. Implement a conversation state manager that:

   - Creates and maintains conversation sessions
   - Stores conversation history
   - Tracks context information
   - Handles session expiration and cleanup

2. Create these specific functions:

   - create_conversation(user_id) -> conversation_id
   - get_conversation(conversation_id) -> conversation
   - update_conversation(conversation_id, message, response)
   - get_conversation_context(conversation_id) -> context

3. Add these features:

   - Efficient storage of conversation state
   - Context extraction from conversation history
   - Session timeout and cleanup
   - User identification (if applicable)

4. Write tests that verify:
   - Conversations are created and retrieved correctly
   - Context is maintained across messages
   - Session management works as expected
   - Cleanup functions correctly

Use best practices for state management in web applications, including proper security considerations and resource management.
```

#### Step 6.3: Integration of Components

```markdown
# Prompt: Integration of Chatbot Components

Integrate all the chatbot components (message processing, text-to-SQL, database queries, result formatting) into a cohesive system. This will ensure all parts work together correctly and provide a seamless user experience.

Requirements:

1. Create an integration layer that:

   - Coordinates the flow between components
   - Handles errors at each step
   - Maintains proper logging
   - Ensures consistent response formatting

2. Implement these specific functions:

   - process_chat_request(user_message, conversation_id) -> response
   - handle_sql_query_intent(message, context) -> response
   - handle_general_question(message, context) -> response
   - format_final_response(component_response) -> user_response

3. Add these features:

   - Error recovery at each integration point
   - Performance monitoring for each component
   - Fallback mechanisms for component failures
   - Consistent response structure

4. Write tests that verify:
   - Full integration works for different query types
   - Errors in one component don't crash the system
   - Performance meets expectations
   - Responses are consistent across different paths

Use best practices for component integration, including proper error handling, logging, and response consistency.
```

#### Step 6.4: Enhanced Features Implementation

```markdown
# Prompt: Enhanced Chatbot Features

Implement enhanced features for the weather chatbot, including visualization generation, analytical capabilities, and improved natural language understanding.

Requirements:

1. Create modules for these enhanced features:

   - Weather data visualization generation
   - Trend analysis for weather patterns
   - Comparative analysis (e.g., month-to-month)
   - Natural language understanding improvements

2. Implement these specific functions:

   - generate_weather_chart(data, chart_type) -> chart_image
   - analyze_weather_trend(data, metric) -> trend_analysis
   - compare_weather_periods(period1, period2, metrics) -> comparison
   - enhance_query_understanding(query) -> enhanced_query

3. Add these visualization types:

   - Temperature trends over time
   - Precipitation patterns
   - Humidity and pressure correlations
   - Wind speed and direction analysis

4. Write tests that verify:
   - Visualizations are generated correctly
   - Analysis produces accurate results
   - Comparisons identify meaningful differences
   - Query understanding improvements work as expected

Use best practices for data visualization and analysis, including proper data validation, appropriate chart types, and clear presentation.
```

### Chunk 7: Testing and Refinement

#### Step 7.1: Comprehensive Test Suite

```markdown
# Prompt: Comprehensive Test Suite

Create a comprehensive test suite for the entire weather ETL and chatbot application. This suite should cover all components and ensure the system works correctly as a whole.

Requirements:

1. Implement tests for these categories:

   - Unit tests for individual functions and classes
   - Integration tests for component interactions
   - End-to-end tests for complete workflows
   - Performance tests for critical operations

2. Create test fixtures for:

   - Database state
   - API responses
   - User messages
   - Expected outputs

3. Test these specific scenarios:

   - Complete ETL pipeline execution
   - Various types of user queries
   - Error handling at different levels
   - Performance under load

4. Implement test utilities for:
   - Test database setup and teardown
   - Mock API responses
   - Conversation simulation
   - Result validation

Use best practices for testing Python applications, including proper test isolation, comprehensive coverage, and meaningful assertions.
```

#### Step 7.2: Documentation

```markdown
# Prompt: Project Documentation

Create comprehensive documentation for the weather ETL and chatbot application. This documentation should cover both user guides and technical documentation.

Requirements:

1. Create these documentation types:

   - User guide for the chatbot interface
   - Technical overview of the system architecture
   - API documentation for internal components
   - Setup and deployment guide

2. Include these specific sections:

   - System requirements and dependencies
   - Installation and configuration instructions
   - Usage examples for the chatbot
   - Troubleshooting guide

3. Add these technical details:

   - Database schema documentation
   - Component interaction diagrams
   - API endpoint specifications
   - Configuration options

4. Format the documentation as:
   - Markdown files in the repository
   - README.md with overview and quick start
   - Detailed guides in docs/ directory
   - Code documentation with docstrings

Use best practices for technical documentation, including clear structure, examples, and appropriate detail level.
```

#### Step 7.3: Performance Optimization

```markdown
# Prompt: Performance Optimization

Identify and implement performance optimizations for the weather ETL and chatbot application. This will improve user experience and reduce resource usage.

Requirements:

1. Optimize these components:

   - Database queries and indexing
   - API request handling and caching
   - Text-to-SQL conversion process
   - Chatbot response generation

2. Implement these specific optimizations:

   - Add appropriate database indexes
   - Implement caching for frequent queries
   - Optimize OpenAI prompt efficiency
   - Improve frontend response rendering

3. Add these performance metrics:

   - Response time monitoring
   - Database query performance tracking
   - API request timing
   - Resource usage monitoring

4. Create tests that verify:
   - Optimizations improve performance as expected
   - No regression in functionality
   - Performance meets requirements under load
   - Resource usage is within acceptable limits

Use best practices for performance optimization, including proper measurement, targeted improvements, and validation of results.
```

#### Step 7.4: Deployment Preparation

```markdown
# Prompt: Deployment Preparation

Prepare the weather ETL and chatbot application for deployment to a production environment. This will ensure the system is ready for real-world use.

Requirements:

1. Create these deployment artifacts:

   - Docker configuration (Dockerfile, docker-compose.yml)
   - Environment configuration templates
   - Deployment scripts
   - Backup and restore procedures

2. Implement these production settings:

   - Security hardening
   - Production-ready database configuration
   - Logging and monitoring setup
   - Proper error handling and fallbacks

3. Add these deployment instructions:

   - Step-by-step deployment guide
   - Configuration checklist
   - Post-deployment verification
   - Maintenance procedures

4. Create scripts for:
   - Database initialization
   - Environment setup
   - Service management
   - Backup and restore

Use best practices for application deployment, including security considerations, environment isolation, and proper documentation.
```

## Conclusion

This implementation plan provides a detailed, step-by-step approach to building the weather ETL and chatbot application. Each step builds incrementally on previous work, ensuring a solid foundation and manageable complexity at each stage.

The prompts are designed for a code-generation LLM and focus on test-driven development, best practices, and proper integration of components. By following this plan, you'll create a robust, maintainable system that meets all the requirements in the specification.

Key principles throughout the implementation:

1. Start with core infrastructure and gradually add functionality
2. Test each component thoroughly before integration
3. Use best practices for security, error handling, and performance
4. Document code and provide clear instructions at each step
5. Ensure all components are properly integrated with no orphaned code

The final result will be a fully functional weather ETL pipeline and AI-powered chatbot that provides valuable insights from weather data through natural language interaction.
