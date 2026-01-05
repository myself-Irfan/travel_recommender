from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import date, timedelta

from travel.services.recommend_service import RecommendService


class RecommendServiceTest(TestCase):
    def setUp(self):
        self.service = RecommendService()
        self.travel_date = date.today() + timedelta(days=3)

    def test_get_value_at_2pm_on_date_found(self):
        times = ["2024-01-15T10:00", "2024-01-15T14:00", "2024-01-15T18:00"]
        values = [20.0, 25.0, 22.0]
        target_date = date(2024, 1, 15)

        result = self.service._get_value_at_2pm_on_date(times, values, target_date)

        self.assertEqual(result, 25.0)

    def test_get_value_at_2pm_on_date_not_found(self):
        times = ["2024-01-15T14:00"]
        values = [25.0]
        target_date = date(2024, 1, 16)

        result = self.service._get_value_at_2pm_on_date(times, values, target_date)

        self.assertIsNone(result)

    @patch('travel.services.recommend_service.WeatherService')
    def test_fetch_metrics_for_date_success(self, mock_weather_service):
        from travel.services.recommend_service import RecommendService

        mock_weather = {
            "forecast": {
                "hourly": {
                    "time": [
                        f"{self.travel_date.isoformat()}T00:00",
                        f"{self.travel_date.isoformat()}T14:00",
                    ],
                    "temperature_2m": [24.0, 25.0],
                }
            },
            "air_quality": {
                "hourly": {
                    "time": [
                        f"{self.travel_date.isoformat()}T00:00",
                        f"{self.travel_date.isoformat()}T14:00",
                    ],
                    "pm2_5": [55.0, 50.0],
                }
            }
        }

        mock_weather_instance = MagicMock()
        mock_weather_instance.get_weather_for_district.return_value = mock_weather

        mock_weather_service.return_value = mock_weather_instance
        service = RecommendService()

        metrics = service._fetch_metrics_for_date(
            "Dhaka", 23.8103, 90.4125, self.travel_date
        )

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics["temp"], 25.0)
        self.assertEqual(metrics["pm25"], 50.0)

        mock_weather_instance.get_weather_for_district.assert_called_once_with(
            district={"name": "Dhaka", "lat": 23.8103, "long": 90.4125}
        )

    @patch.object(RecommendService, '_fetch_metrics_for_date')
    @patch('travel.services.recommend_service.DistrictService')
    def test_recommend_cooler_and_cleaner(self, mock_district_service, mock_fetch_metrics):
        mock_district_service.return_value.get_district_by_name.return_value = {
            "name": "Sylhet",
            "lat": 24.8949,
            "long": 91.8687
        }

        mock_fetch_metrics.side_effect = [
            {"temp": 30.0, "pm25": 120.0},
            {"temp": 22.0, "pm25": 40.0}
        ]

        result = self.service.recommend(
            current_lat=23.8103,
            current_lon=90.4125,
            destination_name="Sylhet",
            travel_date=self.travel_date
        )

        self.assertEqual(result["recommendation"], "Recommended")
        self.assertIn("cooler", result["reason"])
        self.assertIn("better air quality", result["reason"])

    @patch.object(RecommendService, '_fetch_metrics_for_date')
    @patch('travel.services.recommend_service.DistrictService')
    def test_recommend_hotter_and_worse(self, mock_district_service, mock_fetch_metrics):
        mock_district_service.return_value.get_district_by_name.return_value = {
            "name": "Dhaka",
            "lat": 23.8103,
            "long": 90.4125
        }

        mock_fetch_metrics.side_effect = [
            {"temp": 22.0, "pm25": 40.0},
            {"temp": 30.0, "pm25": 120.0}
        ]

        result = self.service.recommend(
            current_lat=24.8949,
            current_lon=91.8687,
            destination_name="Dhaka",
            travel_date=self.travel_date
        )

        self.assertEqual(result["recommendation"], "Not Recommended")
        self.assertIn("better to stay", result["reason"])

    @patch('travel.services.recommend_service.DistrictService')
    def test_recommend_destination_not_found(self, mock_district_service):
        mock_district_service.return_value.get_district_by_name.return_value = None

        result = self.service.recommend(
            current_lat=23.8103,
            current_lon=90.4125,
            destination_name="NonExistent",
            travel_date=self.travel_date
        )

        self.assertEqual(result["recommendation"], "Not Recommended")
        self.assertIn("not found", result["reason"])