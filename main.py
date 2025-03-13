import os
from pathlib import Path
from config.logging_config import configure_logging
from etl.extract import extract_data_from_file
from etl.transform import transform_data
from etl.load import load_data_to_database
from chatbot.bot import Chatbot
from utils.logger import LoggerFactory, log_structured, setup_logger

# Configure the logging system based on environment
log_level = os.environ.get('LOG_LEVEL', 'info')
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure root logger
configure_logging(log_dir=str(log_dir), level=log_level)

# Create a logger for the main application
logger = setup_logger(
    "main",
    log_file=str(log_dir / "application.log")
)

def main():
    """
    Main function to run the ETL-based chatbot application.
    """
    logger.info("Starting ETL-based chatbot application")

    try:
        # Set logging environment based on ENV variable or default to development
        environment = os.environ.get('ENV', 'development')
        LoggerFactory.set_environment(environment)
        logger.info(f"Running in {environment} environment")

        # Extract data
        data_file = "data/sample.txt"
        logger.info(f"Starting extraction from {data_file}")
        raw_data = extract_data_from_file(data_file)

        # Transform data
        logger.info("Starting transformation")
        transformed_data = transform_data(raw_data)

        # Load data
        logger.info("Starting data loading")
        # Mocked database connection for example
        db_connection = {"connection": "mocked"}
        load_status = load_data_to_database(transformed_data, db_connection)

        # Initialize chatbot
        logger.info("Initializing chatbot")
        bot = Chatbot()

        # Example interaction
        sample_query = "Tell me about this dataset"
        logger.info(f"Processing sample query: {sample_query}")
        response = bot.process_query(sample_query)
        print(f"Bot response: {response}")

        # Log structured completion data
        log_structured(
            logger,
            "info",
            "application_complete",
            status="success",
            processing_time=0.5,  # Example value
            data_size=len(raw_data)
        )

        logger.info("ETL-based chatbot application completed successfully")
    except Exception as e:
        # Log structured error data
        log_structured(
            logger,
            "error",
            "application_error",
            error_type=type(e).__name__,
            error_message=str(e)
        )

        logger.error(f"Application failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
