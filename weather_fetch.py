#!/usr/bin/env python3
"""
Weather Data Fetcher: A Secure script for reading and analysing weather information from the OpenWeatherMap API.

This script shows how to handle errors correctly, store API keys securely, and process data from a public API efficiently.
"""

import os
import sys
import requests
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("weather_fetch.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("WeatherFetcher")


class WeatherFetcher:
    """Class to fetch and process weather data from OpenWeatherMap API."""

    # Correct API endpoint - please note that correct version should be v2.5
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        """Initialize the WeatherFetcher with API key from environment variables."""
        # Load .env file
        load_dotenv()

        # Get API key use env var for security
        self.api_key = os.getenv("OPENWEATHERKEY")
        if not self.api_key:
            logger.error(
                "API key not found. Ensure OPENWEATHERMAP_API_KEY is set in .env file"
            )
            raise ValueError(
                "API key not found. Set OPENWEATHERMAP_API_KEY in .env file"
            )

        logger.info("WeatherFetcher initialized successfully")

    def fetch_weather_per_city(self, city_name):
        """
        Retrieve weather information for a given city.

        Args: city_name (str):
            The city's name for which meteorological information is to be retrieved

        Returns:
            dict: Weather data that has been processed

        Raises:
            ConnectionError: If a network problem exists
            ValueError: If an unexpected response format
            KeyError: If the response requests do not contain expected data
            requests.exceptions.HTTPError: If an HTTP error occurs
        """
        logger.info(f"Retrieving weather data for {city_name}")

        try:
            # Prepare request args
            params = {
                "q": city_name.strip(),  # Remove whitespace in words
                "appid": self.api_key,
                "units": "metric",  # Use Celsius as metric
            }

            # API request
            response = requests.get(self.BASE_URL, params=params)

            logger.info(f"API status code for response: {response.status_code}")

            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Process the data
            processed_data = self._weather_request_data(data)

            logger.info(
                f"Successfully fetched and processed weather data for {city_name}"
            )
            return processed_data

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Network error while fetching data: {str(e)}")
            raise ConnectionError(f"Failed to connect to weather service: {str(e)}")

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed. Check your API key")
                raise ValueError("Invalid API key")
            elif response.status_code == 404:
                logger.error(f"City '{city_name}' not found")
                raise ValueError(
                    f"City '{city_name}' not found. Try adding country code like: '{city_name},US'"
                )
            else:
                logger.error(f"HTTP error occurred: {str(e)}")
                logger.error(f"Response content: {response.text}")
                raise

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            raise ValueError(f"Invalid response from weather service: {str(e)}")

        except (KeyError, ValueError) as e:
            logger.error(f"Error processing weather data: {str(e)}")
            raise

    def _weather_request_data(self, data):
        """
        Convert unprocessed weather data into a format that is more practical.

        Args:
            data (dict):OpenWeatherMap API raw data

        Returns:
            dict: Weather data processed using specific fields

        Raises:
            KeyError: If the data contains missing expected fields,
        """
        try:
            processed_data = {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": {
                    "current": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "min": data["main"]["temp_min"],
                    "max": data["main"]["temp_max"],
                },
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind": {
                    "speed": data["wind"]["speed"],
                    "direction": data["wind"].get("deg", "N/A"),
                },
                "weather_description": data["weather"][0]["description"],
                "weather_main": data["weather"][0]["main"],
                "timestamp": datetime.now().isoformat(),
            }

            return processed_data

        except KeyError as e:
            logger.error(f"Missing expected field in weather data: {str(e)}")
            raise KeyError(f"Missing expected field in weather data: {str(e)}")


def save_weather_json(data, filename=None):
    """
    Convert weather information to a JSON file.

    Args:
        data (dict): Weather data that has been processed
        filename (optional, str): unique filename. uses a time-stamped file by default.

    Returns:
        str: Path to the saved file
    """
    if filename is None:
        city = data["city"].lower().replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_{city}_{timestamp}.json"

    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Weather data saved to {filename}")
        return filename
    except IOError as e:
        logger.error(f"Error saving weather data to file: {str(e)}")
        raise IOError(f"Failed to save weather data: {str(e)}")


def main():
    """Main function to run the weather fetcher."""
    try:
        # Create weather fetcher instance
        weather_fetcher = WeatherFetcher()

        # Get city from command line argument or use default
        if len(sys.argv) > 1:
            city = sys.argv[1]
        else:
            city = input(
                "Enter city name (you can add country code like 'London,GB'): "
            )

        # Fetch and process weather data
        weather_data = weather_fetcher.fetch_weather_per_city(city)

        # Print a summary of the weather data
        print(f"\nWeather in {weather_data['city']}, {weather_data['country']}:")
        print(
            f"Temperature: {weather_data['temperature']['current']}°C "
            f"(feels like {weather_data['temperature']['feels_like']}°C)"
        )
        print(f"Condition: {weather_data['weather_description']}")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Wind Speed: {weather_data['wind']['speed']} m/s")

        # Save the weather data to a file
        filename = save_weather_json(weather_data)
        print(f"\nDetailed weather data saved to {filename}")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
