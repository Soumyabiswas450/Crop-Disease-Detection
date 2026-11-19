
import requests


def get_location(location_name):
    """Convert manually entered location into coordinates."""

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location_name,
        "count": 5,
        "language": "en",
        "format": "json",
        "countryCode": "IN"
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    locations = response.json().get("results", [])

    if not locations:
        return None

    return locations[0]


def get_weather(latitude, longitude):
    """Fetch current weather and 7-day forecast."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m"
        ],

        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_hours",
            "precipitation_probability_max"
        ],

        "forecast_days": 7,
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()


def get_weather_data(location_name):
    """Fetch weather using a manually entered location."""

    location = get_location(location_name)

    if not location:
        return None

    weather = get_weather(
        location["latitude"],
        location["longitude"]
    )

    return {
        "location": location,
        "weather": weather
    }
