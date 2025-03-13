"""
Tests for the location validator utilities.
"""

import unittest
import pytest
from utils.location_validator import validate_city_format

class TestLocationValidator(unittest.TestCase):
    """Test cases for location validator functions."""

    def test_validate_city_format_with_full_format(self):
        """Test with city, state, and country."""
        result = validate_city_format("New York,NY,US")
        self.assertEqual(result, "New York,NY,US")

        # Test with spaces around commas
        result = validate_city_format("New York , NY , US")
        self.assertEqual(result, "New York,NY,US")

    def test_validate_city_format_with_city_state(self):
        """Test with city and state."""
        result = validate_city_format("Louisville,KY")
        self.assertEqual(result, "Louisville,KY,US")

    def test_validate_city_format_with_city_country(self):
        """Test with city and country."""
        result = validate_city_format("London,GB")
        self.assertEqual(result, "London,GB")

        # Test lowercase country code
        result = validate_city_format("Paris,fr")
        self.assertEqual(result, "Paris,FR")

    def test_validate_city_format_with_city_only(self):
        """Test with just city name."""
        result = validate_city_format("Chicago")
        self.assertEqual(result, "Chicago,US")

    def test_validate_city_format_with_empty_input(self):
        """Test with empty input."""
        result = validate_city_format("")
        self.assertEqual(result, "Louisville,KY,US")

        result = validate_city_format(None)
        self.assertEqual(result, "Louisville,KY,US")

    def test_validate_city_format_with_invalid_input(self):
        """Test with invalid input format."""
        result = validate_city_format(",,,")
        self.assertEqual(result, "Louisville,KY,US")

@pytest.mark.parametrize("city_input,expected", [
    ("New York,NY,US", "New York,NY,US"),
    ("London,GB", "London,GB"),
    ("Paris, France", "Paris,France,US"),
    ("Tokyo, JP", "Tokyo,JP"),
    ("", "Louisville,KY,US"),
])
def test_location_format(city_input, expected):
    """Parametrized test for validate_city_format function."""
    assert validate_city_format(city_input) == expected
