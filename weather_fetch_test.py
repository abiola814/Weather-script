#!/usr/bin/env python3
"""
set of tests for the script Weather Fetcher.

The weather_fetch.py script's functionality under
various scenarios is checked by the unit tests in this file.

"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock
from weather_fetch import WeatherFetcher, save_weather_json
import requests


class TestWeatherFetcher(unittest.TestCase):
    """Test cases for the WeatherFetcher class."""

    def config(self):
        """Set up test fixtures before each test method."""
        # Create a mock environment variable for testing
        os.environ["OPENWEATHERKEY"] = "test_api_key"

        # Sample response data for mocking API calls
        self.sample_response = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 15.5,
                "feels_like": 14.8,
                "temp_min": 13.2,
                "temp_max": 17.1,
                "humidity": 76,
                "pressure": 1012,
            },
            "wind": {"speed": 4.1, "deg": 250},
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
        }

    def cleanUp(self):
        """Clean up after each test method."""
        # Remove environment variable
        if "OPENWEATHERKEY" in os.environ:
            del os.environ["OPENWEATHERKEY"]

        # Remove any test files created
        for file in os.listdir("."):
            if file.startswith("weather_test_") and file.endswith(".json"):
                os.remove(file)

    @patch("weather_fetch.requests.get")
    def test_weather_fetch_per_city_success(self, mock_get):
        """Verify that the weather data fetching was successful."""
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = self.sample_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Initialize weather fetcher and fetch data
        fetcher = WeatherFetcher()
        result = fetcher.weather_fetch_per_city("London")

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]["params"]
        self.assertEqual(call_args["q"], "London")
        self.assertEqual(call_args["appid"], "test_api_key")

        # Verify the result contains expected data
        self.assertEqual(result["city"], "London")
        self.assertEqual(result["country"], "GB")
        self.assertEqual(result["temperature"]["current"], 15.5)
        self.assertEqual(result["weather_description"], "scattered clouds")

    @patch("weather_fetch.requests.get")
    def test_weather_fetch_per_city_city_not_found(self, mock_get):
        """Test how to handle the error "city not found."""
        # Configure the mock to return a 404 error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "404 Client Error: Not Found for url: test_url"
        )
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Initialize weather fetcher and attempt to fetch data
        fetcher = WeatherFetcher()

        # Expect ValueError to be raised for city not found
        with self.assertRaises(ValueError) as context:
            fetcher.weather_fetch_per_city("NonExistentCity")

        self.assertIn("not found", str(context.exception))

    @patch("weather_fetch.requests.get")
    def test_weather_fetch_per_city_network_error(self, mock_get):
        """Test how network errors are handled"""
        # Configure the mock to raise a ConnectionError
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        # Initialize weather fetcher and attempt to fetch data
        fetcher = WeatherFetcher()

        # Expect ConnectionError to be raised for network issues
        with self.assertRaises(ConnectionError):
            fetcher.weather_fetch_per_city("London")

    @patch("weather_fetch.requests.get")
    def test_weather_fetch_per_city_invalid_api_key(self, mock_get):
        """Test handling of invalid API key error."""
        # Configure the mock to return a 401 error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "401 Client Error: Unauthorized for url: test_url"
        )
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        # Initialize weather fetcher and attempt to fetch data
        fetcher = WeatherFetcher()

        # Expect ValueError to be raised for invalid API key
        with self.assertRaises(ValueError) as context:
            fetcher.weather_fetch_per_city("London")

        self.assertIn("Invalid API key", str(context.exception))

    def test_weather_request_data(self):
        """Test processing of raw weather data."""
        fetcher = WeatherFetcher()
        processed_data = fetcher._weather_request_data(self.sample_response)

        # Verify processed data has expected structure and values
        self.assertEqual(processed_data["city"], "London")
        self.assertEqual(processed_data["temperature"]["current"], 15.5)
        self.assertEqual(processed_data["humidity"], 76)
        self.assertEqual(processed_data["wind"]["speed"], 4.1)
        self.assertEqual(processed_data["weather_main"], "Clouds")

    def test_weather_request_data_missing_fields(self):
        """Test handling of missing fields in weather data."""
        # Create data with missing fields
        incomplete_data = {
            "name": "London",
            "sys": {"country": "GB"},
            "main": {
                "temp": 15.5
                # Missing other fields
            },
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
        }

        fetcher = WeatherFetcher()

        # Expect KeyError for missing fields
        with self.assertRaises(KeyError):
            fetcher._weather_request_data(incomplete_data)

    def test_save_weather_json(self):
        """Test saving weather data to a file."""
        test_data = {
            "city": "Test City",
            "country": "TC",
            "temperature": {
                "current": 20.5,
                "feels_like": 19.8,
                "min": 18.0,
                "max": 22.0,
            },
            "humidity": 65,
            "pressure": 1015,
            "wind": {"speed": 3.5, "direction": 180},
            "weather_description": "clear sky",
            "weather_main": "Clear",
            "timestamp": "2023-01-01T12:00:00",
        }

        filename = "weather_test_save.json"
        saved_file = save_weather_json(test_data, filename)

        # Verify file was created
        self.assertTrue(os.path.exists(saved_file))

        # Verify file contains correct data
        with open(saved_file, "r") as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data, test_data)

    def test_missing_api_key(self):
        """Test handling of missing API key."""
        # Remove API key from environment
        if "OPENWEATHERKEY" in os.environ:
            del os.environ["OPENWEATHERKEY"]

        # Expect ValueError when API key is missing
        with self.assertRaises(ValueError) as context:
            WeatherFetcher()

        self.assertIn("API key not found", str(context.exception))


if __name__ == "__main__":
    unittest.main()
