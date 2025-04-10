# Weather ETL Based Chatbot

A Python-based ETL pipeline that collects weather data and provides a chatbot interface for querying weather information.

## Features

- ETL Pipeline for weather data collection and processing
- Database storage for historical weather data
- OpenAI-powered chatbot for natural language queries
- RESTful API endpoints
- Web interface for interaction

## Prerequisites

- Python 3.9+
- PostgreSQL
- OpenWeatherMap API key
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd weather-etl-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
make install
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file with your configuration values.

## Usage

1. Initialize the database:
```bash
make init-db
```

2. Load sample data (optional):
```bash
make sample-data
```

3. Run the application:
```bash
make run
```

## Development

- Format code:
```bash
make format
```

- Run linting:
```bash
make lint
```

- Run tests:
```bash
make test
```

## Project Structure

```
.
├── chatbot/          # Chatbot implementation
├── database/         # Database models and initialization
├── etl/             # ETL pipeline implementation
├── web/             # Web interface
├── config/          # Configuration files
├── utils/           # Utility functions
├── tests/           # Test files
├── notebooks/       # Jupyter notebooks for analysis
└── logs/           # Application logs
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
