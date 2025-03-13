# Weather ETL Chatbot

A comprehensive data pipeline and chatbot application that collects weather data for Louisville, KY, stores it in a PostgreSQL database, and provides a natural language interface for querying the data.

## Features

- Automated ETL pipeline for weather data collection using OpenWeatherMap API
- PostgreSQL database for data storage and retrieval
- Flask-based web application with chatbot interface
- Natural language processing using OpenAI's GPT-4o-mini

## Project Structure

```
weather_etl_chatbot/
├── config/          # Configuration files
├── database/        # Database utilities and scripts
├── dev/             # Other dev related scripts
├── etl/             # ETL pipeline code
├── files/           # any misc project related files
├── etl/             # ETL pipeline code
├── notebooks/       # Jupyter notebooks for data analysis
├── notes/           # Notes and documentation
├── web/             # Flask web application
└── tests/           # Test cases
```

### Directory Structure

```
weather_etl_chatbot/
├── .env.example              # Example environment variables file
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup file
├── config/                   # Configuration files
│   ├── __init__.py
│   ├── settings.py           # Main settings file
│   └── logging_config.py     # Logging configuration
├── database/                 # Database utilities and scripts
│   ├── __init__.py
│   ├── db_connector.py       # Database connection utilities
│   ├── models.py             # Database models
│   └── schema.sql            # SQL schema for PostgreSQL
├── etl/                      # ETL pipeline code
│   ├── __init__.py
│   ├── weather_collector.py  # Weather data collector
│   ├── data_processor.py     # Data processing utilities
│   └── data_loader.py        # Data loading utilities
├── web/                      # Flask web application
│   ├── __init__.py
│   ├── app.py                # Flask application entry point
│   ├── chatbot.py            # Chatbot logic
│   ├── routes.py             # Flask routes
│   └── templates/            # HTML templates
│       ├── index.html
│       └── chat.html
└── tests/                    # Test cases
    ├── __init__.py
    ├── test_weather_collector.py  # Tests for weather collector
    ├── test_data_processor.py     # Tests for data processing
    └── test_chatbot.py            # Tests for chatbot functionality
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- OpenWeatherMap API key
- OpenAI API key

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/weather_etl_chatbot.git
cd weather_etl_chatbot
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` and add your API keys and database credentials.

5. Install the package in development mode:

```bash
pip install -e .
```

6. Initialize the database:

```bash
psql -U your_username -d your_database -f database/schema.sql
```

eg: `psql -U vamsi_mbmax -d weather_db -f database/schema.sql`

## Usage

### Running the ETL Pipeline

```bash
python -m etl.weather_collector
```

### Starting the Web Application

```bash
python -m web.app
```

Then navigate to `http://localhost:5000` in your web browser.

## Testing

```bash
pytest
```

## License

[MIT](LICENSE)
