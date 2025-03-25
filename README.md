# Weather Data Fetcher

Weather data is retrieved from the OpenWeatherMap API, processed, and saved by a secure Python script. This project exemplifies strong error management, safe API key handling, and appropriate data processing.



## Prerequisites

- Python 3.11 or higher
- OpenWeatherMap API key ([OpenWeatherMap](https://home.openweathermap.org/users/sign_up))


## Installation

1. Clone this repo:
   ```
   git clone https://github.com/abiola814/Weather-script.git
   cd weather-script
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file based on the provided `.env.example`
   - Add your OpenWeatherMap API key to the file:
     ```
     OPENWEATHERKEY=your_key_from_open_weather
     ```
   - Please make sure No quotes or spaces in the environment variable format


## Attributes

- Fetching of weather data securely from OpenWeatherMap API
- Proper storing of environment secret i.e not hardcoded
- Process and format weather data into a user-friendly structure
- Transforming and format of weather response data for 
- loading of user-friendly data to json
- Comprehensive error handling for network issues, API errors, and data processing
- Logging and monitoring
- perform unit test for weather script

## Usage

### Basic Usage

Run the script with a city name as an argument:

```
python weather_fetch.py paris
```

If you don't enter a city, the script will ask you to do so:

```
python weather_fetch.py
Enter city name (you can add country code like 'London,GB'): Paris
```

### Sample Output

The script displays a summary of the weather data:

```
Weather in Paris, FR:
Temperature: 8.77°C (feels like 6.43°C)
Condition: overcast clouds
Humidity: 83%
Wind Speed: 4.12 m/s

Detailed weather data saved to weather_<name of the city e.g london>_20250325_123045.json
```


For additional processing or analysis, the entire set of data is saved to a JSON file.

## Running Tests

Run the test script to confirm the python script's functionality:

```
python -m unittest test_weather_fetcher.py
```

## Project Structure

- `weather_fetch.py` - Main script with the WeatherFetcher class and utility functions
- `weather_fetch_test.py` - Unit tests for all major components
- `.env` - Environment variables file
- `.env.example` - Example environment secret file
- `requirements.txt` - List of Python dependencies
- `README.md` - Weather Script documentation

## Security Considerations

- API keys are kept in environment variables rather than code.
- Sensitive information is not shown by error messages;
- Input validation guards against possible injection attacks
- Handling exceptions to guarantee seamless functioning even in the event of an issue

## Troubleshooting

If you encounter issues:

1. Confirm that your API key is active and accurate.
2. Include a country code (for example, "Paris,FR" rather than just "Paris") for cities with similar names.
3. For comprehensive error information, examine the logs in "weather_fetcher.log".
4. Verify that the `.env` file and the script are located in the same directory.
5. Verify that you have the Python-Dotenv package installed.

## License

MIT License - See LICENSE file for details