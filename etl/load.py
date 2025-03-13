from utils.logger import get_component_logger, log_etl_function

# Create a logger for this module
logger = get_component_logger('etl', 'load')

@log_etl_function
def load_data_to_database(data, db_connection):
    """
    Load transformed data to a database.

    Args:
        data: Transformed data to be loaded
        db_connection: Database connection object

    Returns:
        Status of the loading operation
    """
    logger.info("Loading data to database")
    try:
        # Implementation for data loading
        # Example: db_connection.insert(data)
        logger.debug(f"Successfully loaded {len(data)} bytes of data to database")
        return True
    except Exception as e:
        logger.error(f"Error loading data to database: {str(e)}")
        raise
