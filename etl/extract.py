"""
ETL Extract module responsible for extracting data from various sources.

This module is imported dynamically by the ETL pipeline during the extract phase.
It's not directly imported in static imports but loaded at runtime.

Provides a standardized interface for extracting data from APIs, files, and other sources.

Usage as standalone script:
    python -m etl.extract path/to/file.json
    python -m etl.extract --url https://api.example.com/data
"""

# Note: This file is loaded dynamically in the ETL pipeline and is essential for the application.

import sys
import os
import json
import argparse
from pathlib import Path

# Add project root to Python path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.logger import get_component_logger, log_etl_function

# Create a logger for this module
logger = get_component_logger('etl', 'extract')

@log_etl_function
def extract_data_from_file(file_path):
    """
    Extract data from a given file.

    Args:
        file_path: Path to the file to extract data from

    Returns:
        Extracted data
    """
    logger.info(f"Extracting data from file: {file_path}")
    try:
        # Implementation for data extraction
        with open(file_path, 'r', encoding='utf-8') as f:
            extension = Path(file_path).suffix.lower()

            if extension == '.json':
                data = json.load(f)
                logger.info(f"Successfully extracted JSON data with {len(data) if isinstance(data, (list, dict)) else 'scalar'} entries")
                return data
            else:
                data = f.read()
                logger.debug(f"Successfully extracted {len(data)} characters of data")
                return data
    except Exception as e:
        logger.error(f"Error extracting data from {file_path}: {str(e)}")
        raise

@log_etl_function
def extract_data_from_url(url, headers=None, params=None):
    """
    Extract data from a URL.

    Args:
        url: URL to extract data from
        headers: Optional headers for the request
        params: Optional query parameters

    Returns:
        Extracted data
    """
    import requests

    logger.info(f"Extracting data from URL: {url}")
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            data = response.json()
            logger.info(f"Successfully extracted JSON data with {len(data) if isinstance(data, (list, dict)) else 'scalar'} entries")
        else:
            data = response.text
            logger.info(f"Successfully extracted {len(data)} characters from URL")

        return data
    except Exception as e:
        logger.error(f"Error extracting data from {url}: {str(e)}")
        raise

def display_data_preview(data, max_items=5, max_str_length=100):
    """Display a preview of the extracted data."""
    if isinstance(data, dict):
        print("\nData Preview (Dict):")
        for i, (key, value) in enumerate(list(data.items())[:max_items]):
            value_str = str(value)
            if len(value_str) > max_str_length:
                value_str = value_str[:max_str_length] + "..."
            print(f"  {key}: {value_str}")
        if len(data) > max_items:
            print(f"  ... and {len(data) - max_items} more items")

    elif isinstance(data, list):
        print("\nData Preview (List):")
        for i, item in enumerate(data[:max_items]):
            item_str = str(item)
            if len(item_str) > max_str_length:
                item_str = item_str[:max_str_length] + "..."
            print(f"  {i}: {item_str}")
        if len(data) > max_items:
            print(f"  ... and {len(data) - max_items} more items")

    elif isinstance(data, str):
        print("\nData Preview (String):")
        if len(data) > max_str_length:
            print(f"  {data[:max_str_length]}...")
        else:
            print(f"  {data}")
        print(f"  Total length: {len(data)} characters")

    else:
        print("\nData Preview:")
        print(f"  {str(data)[:max_str_length]}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Extract data from various sources')
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('file', nargs='?', help='Path to the file to extract data from')
    source_group.add_argument('--url', help='URL to extract data from')
    parser.add_argument('--output', '-o', help='Output file to save the extracted data')
    parser.add_argument('--preview', '-p', action='store_true', help='Preview the extracted data')
    return parser.parse_args()

def main():
    """Main function to run the extraction process from command line."""
    args = parse_args()

    try:
        # Extract data
        if args.file:
            print(f"Extracting data from file: {args.file}")
            data = extract_data_from_file(args.file)
        elif args.url:
            print(f"Extracting data from URL: {args.url}")
            data = extract_data_from_url(args.url)

        # Show preview if requested
        if args.preview:
            display_data_preview(data)

        # Save output if requested
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix.lower() == '.json' and isinstance(data, (dict, list)):
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(data))

            print(f"Data saved to {args.output}")

        print("Extraction completed successfully")
        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Extraction failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
