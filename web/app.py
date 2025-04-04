"""
Main Flask application for the Weather ETL Chatbot.
Initializes the Flask app, registers routes, and starts the server.
"""

import logging
from flask import Flask
from web.routes import register_routes
from config.settings import FLASK_CONFIG, TEMPLATES_DIR, STATIC_DIR

# Import logging utilities
from utils import get_component_logger
from config.logging_config import configure_root_logger

# Configure the root logger
configure_root_logger()

# Create a logger for this module
logger = get_component_logger('web', 'app')

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__,
                template_folder=TEMPLATES_DIR,
                static_folder=STATIC_DIR)

    # Load configuration
    app.config.update(FLASK_CONFIG)

    # Register routes
    register_routes(app)

    return app

def main():
    """Run the Flask application."""
    app = create_app()
    logger.info("Starting the Weather ETL Chatbot web application")
    app.run(host="0.0.0.0", port=5005)

if __name__ == "__main__":
    # Configure basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
