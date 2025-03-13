"""
Utility functions for the chatbot module.
"""

from openai import OpenAI
from config.settings import OPENAI_API_KEY
from utils.logger import get_component_logger

# Set up logger
logger = get_component_logger('web', 'chatbot_utils')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def retrieve_response_by_id(response_id):
    """
    Retrieve an OpenAI response by its ID.

    Args:
        response_id (str): The ID of the response to retrieve

    Returns:
        Response object or None if retrieval fails
    """
    try:
        logger.info(f"Retrieving response with ID: {response_id}")
        response = client.responses.retrieve(response_id)

        logger.info(f"Successfully retrieved response {response_id}")
        return response
    except Exception as e:
        logger.error(f"Error retrieving response {response_id}: {e}")
        return None

def get_response_history(limit=10):
    """
    Get recent responses from the OpenAI API.

    Note: This is a placeholder as the OpenAI API doesn't currently
    provide a list endpoint for responses, but you could implement
    a local database to store response IDs.

    Args:
        limit (int): Maximum number of responses to return

    Returns:
        list: Most recent response objects or empty list if error
    """
    # This would be replaced with actual implementation if/when
    # OpenAI provides a list endpoint for responses
    logger.warning("Response history listing not currently available through the API")
    return []
