from utils.logger import get_component_logger, log_etl_function

# Create a logger for this module
logger = get_component_logger('etl', 'transform')

@log_etl_function
def transform_data(data):
    """
    Transform the input data.

    Args:
        data: Raw data to be transformed

    Returns:
        Transformed data
    """
    logger.info("Transforming data")
    try:
        # Implementation for data transformation
        transformed_data = data.lower()  # Example transformation
        logger.debug("Data transformation completed successfully")
        return transformed_data
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        raise
