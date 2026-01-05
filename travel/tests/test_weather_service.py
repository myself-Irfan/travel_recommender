from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from rest_framework import status

from travel.services.weather_service import WeatherService


class WeatherServiceTest(TestCase):
    def setUp(self):
        cache.clear()
        self.service = WeatherService()
        self.mock_forecast = {
            "hourly": {
                "time": ["2024-01-01T14:00", "2024-01-02T14:00"],
                "temperature_2m": [25.5, 26.0]
            }
        }
        self.mock_air_quality = {
            "hourly": {
                "time": ["2024-01-01T14:00", "2024-01-02T14:00"],
                "pm2_5": [50.0, 55.0]
            }
        }

    def tearDown(self):
        cache.clear()

    @patch('travel.services.weather_service.ExternalApiService')
    def test_get_forecast_success(self, mock_api_service):
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = self.mock_forecast

        mock_api_service.return_value.handle_get.return_value = mock_response

        forecast = self.service.get_forecast(
            district_name="Dhaka",
            lat=23.8103,
            lon=90.4125
        )

        self.assertIsNotNone(forecast)
        self.assertIn("hourly", forecast)

    @patch('travel.services.weather_service.ExternalApiService')
    def test_get_air_quality_success(self, mock_api_service):
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = self.mock_air_quality

        mock_api_service.return_value.handle_get.return_value = mock_response

        air_quality = self.service.get_air_quality(
            district_name="Dhaka",
            lat=23.8103,
            lon=90.4125
        )

        self.assertIsNotNone(air_quality)
        self.assertIn("hourly", air_quality)

    @patch.object(WeatherService, 'get_forecast')
    @patch.object(WeatherService, 'get_air_quality')
    def test_get_weather_for_district_with_cache(self, mock_air, mock_forecast):
        mock_forecast.return_value = self.mock_forecast
        mock_air.return_value = self.mock_air_quality

        district = {"name": "Dhaka", "lat": 23.8103, "long": 90.4125}

        weather1 = self.service.get_weather_for_district(district=district)
        weather2 = self.service.get_weather_for_district(district=district)

        mock_forecast.assert_called_once()
        mock_air.assert_called_once()

        self.assertEqual(weather1, weather2)

    @patch.object(WeatherService, 'get_weather_for_district')
    def test_batch_get_weather(self, mock_get_weather):
        mock_get_weather.return_value = {
            "district_name": "Dhaka",
            "forecast": self.mock_forecast,
            "air_quality": self.mock_air_quality
        }

        districts = [
            {"name": "Dhaka", "lat": 23.8103, "long": 90.4125},
            {"name": "Chittagong", "lat": 22.3569, "long": 91.7832}
        ]

        results = self.service.batch_get_weather(districts)

        self.assertEqual(len(results), 2)
        self.assertEqual(mock_get_weather.call_count, 2)