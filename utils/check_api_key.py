"""
Utility script to check if the OpenWeatherMap API key is properly configured.
"""

import os
import sys
from pathlib import Path

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import setup_logger

# Create a logger
logger = setup_logger("api_key_checker")

def check_api_key():
    """Check if the OpenWeatherMap API key is configured."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")

    if not api_key:
        logger.error("OpenWeatherMap API key not found in environment variables.")
        print("\n❌ ERROR: OpenWeatherMap API key not configured!")
        print("Please set the OPENWEATHERMAP_API_KEY environment variable.")
        print("\nYou can do this by running:")
        print("  export OPENWEATHERMAP_API_KEY=your_api_key_here")
        print("\nOr add it to your .env file:\n  OPENWEATHERMAP_API_KEY=your_api_key_here\n")
        return False

    logger.info("OpenWeatherMap API key found in environment variables.")
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
    print(f"\n✅ OpenWeatherMap API key configured: {masked_key}")
    return True

if __name__ == "__main__":
    check_api_key()
