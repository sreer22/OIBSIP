import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests

from weather_app import (
    GEOCODING_URL,
    FORECAST_URL,
    WeatherError,
    WeatherService,
    convert_temperature,
    weather_description,
)


class WeatherHelpersTests(unittest.TestCase):
    def test_celsius_fahrenheit_conversion(self):
        self.assertEqual(convert_temperature(0, "C"), 0)
        self.assertEqual(convert_temperature(0, "F"), 32)
        self.assertEqual(convert_temperature(100, "F"), 212)

    def test_invalid_temperature_unit_is_rejected(self):
        with self.assertRaises(ValueError):
            convert_temperature(12, "K")

    def test_weather_code_maps_to_description_and_symbol(self):
        self.assertEqual(weather_description(0), ("Clear sky", "☀"))
        self.assertEqual(weather_description(999)[0], "Unknown conditions")


class WeatherServiceTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock()
        self.service = WeatherService(session=self.session)

    def test_empty_location_is_rejected_without_network_request(self):
        with self.assertRaisesRegex(WeatherError, "Enter a city"):
            self.service.find_location("   ")
        self.session.get.assert_not_called()

    def test_location_lookup_returns_first_match(self):
        response = Mock()
        response.json.return_value = {
            "results": [
                {
                    "name": "London",
                    "admin1": "England",
                    "country": "United Kingdom",
                    "latitude": 51.5,
                    "longitude": -0.1,
                    "timezone": "Europe/London",
                }
            ]
        }
        self.session.get.return_value = response

        place = self.service.find_location(" London ")

        self.assertEqual(place["name"], "London")
        self.session.get.assert_called_once()
        self.assertEqual(self.session.get.call_args.args[0], GEOCODING_URL)
        self.assertEqual(self.session.get.call_args.kwargs["params"]["name"], "London")

    def test_location_not_found_is_clear_error(self):
        response = Mock()
        response.json.return_value = {}
        self.session.get.return_value = response

        with self.assertRaisesRegex(WeatherError, "No matching city"):
            self.service.find_location("Nowhere")

    def test_location_timeout_is_clear_error(self):
        self.session.get.side_effect = requests.Timeout()
        with self.assertRaisesRegex(WeatherError, "timed out"):
            self.service.find_location("London")

    def test_forecast_parses_current_hourly_and_daily_values(self):
        times = [f"2026-10-06T{hour:02d}:00" for hour in range(24)]
        response = Mock()
        response.json.return_value = {
            "timezone": "Europe/London",
            "current": {
                "time": "2026-10-06T10:30",
                "temperature_2m": 15.0,
                "relative_humidity_2m": 65,
                "apparent_temperature": 14.0,
                "weather_code": 2,
                "wind_speed_10m": 9.5,
            },
            "hourly": {
                "time": times,
                "temperature_2m": [10.0 + i for i in range(24)],
                "relative_humidity_2m": [50 + i for i in range(24)],
                "weather_code": [2] * 24,
            },
            "daily": {
                "time": [f"2026-10-{day:02d}" for day in range(6, 12)],
                "temperature_2m_max": [20, 21, 22, 23, 24, 25],
                "temperature_2m_min": [10, 11, 12, 13, 14, 15],
                "weather_code": [0, 1, 2, 3, 61, 0],
            },
        }
        self.session.get.return_value = response
        place = {
            "name": "London",
            "admin1": "England",
            "country": "United Kingdom",
            "latitude": 51.5,
            "longitude": -0.1,
            "timezone": "Europe/London",
        }

        report = self.service.fetch_forecast(place)

        self.assertEqual(report.location, "London, England, United Kingdom")
        self.assertEqual(report.timezone, "Europe/London")
        self.assertEqual(report.current["temperature_2m"], 15.0)
        self.assertEqual(len(report.hourly), 6)
        self.assertEqual(report.hourly[0]["time"], "2026-10-06T11:00")
        self.assertEqual(len(report.daily), 5)
        self.assertEqual(self.session.get.call_args.args[0], FORECAST_URL)

    def test_forecast_http_failure_is_clear_error(self):
        response = Mock()
        response.status_code = 500
        response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
        self.session.get.return_value = response

        with self.assertRaisesRegex(WeatherError, "weather service returned an error"):
            self.service.fetch_forecast(
                {"name": "London", "latitude": 1, "longitude": 1}
            )

    def test_ip_lookup_returns_city_and_country(self):
        response = Mock()
        response.json.return_value = {
            "city": "London",
            "region": "England",
            "country": "GB",
        }
        self.session.get.return_value = response

        self.assertEqual(self.service.locate_by_ip(), "London, England, GB")


if __name__ == "__main__":
    unittest.main()
