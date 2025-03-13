"""
Utility script to test city format for OpenWeatherMap API.
"""

import sys
from pathlib import Path
import argparse

# Add project root to path if needed
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.location_validator import test_location_format

def main():
    """Test city format for OpenWeatherMap API."""
    parser = argparse.ArgumentParser(description="Test city format for OpenWeatherMap API")
    parser.add_argument('city', help='City to test (e.g., "London", "Paris,FR", "Louisville,KY,US")')
    args = parser.parse_args()

    print(f"\nTesting city format: '{args.city}'")
    print("--------------------------------")

    result = test_location_format(args.city)

    if result['valid']:
        print(f"✅ Success! {result['message']}")
        if 'location' in result:
            loc = result['location']
            print(f"\nDetails:")
            print(f"  - Name: {loc.get('name', 'N/A')}")
            print(f"  - Country: {loc.get('country', 'N/A')}")
            print(f"  - State: {loc.get('state', 'N/A')}")
            print(f"  - Coordinates: lat={loc.get('lat', 'N/A')}, lon={loc.get('lon', 'N/A')}")
    else:
        print(f"❌ Error: {result['message']}")
        print("\nSuggestions:")
        print("  - Check city spelling")
        print("  - For US cities, use format: 'City,State,US' (e.g., 'Louisville,KY,US')")
        print("  - For other countries, use format: 'City,CountryCode' (e.g., 'Paris,FR')")
        print("  - Ensure your API key is correctly set in the environment")

    print("\nFormatted city string to use: " + result['formatted'])

if __name__ == "__main__":
    main()
