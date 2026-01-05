from django.test import TestCase
from unittest.mock import patch

from travel.services.best_districts_service import BestDistrictsService


class BestDistrictsServiceTest(TestCase):
    def setUp(self):
        self.service = BestDistrictsService()
        self.mock_weather_data = [
            {
                "district_name": "Sylhet",
                "forecast": {
                    "hourly": {
                        "time": [
                            "2024-01-01T14:00", "2024-01-02T14:00",
                            "2024-01-03T14:00", "2024-01-04T14:00",
                            "2024-01-05T14:00", "2024-01-06T14:00",
                            "2024-01-07T14:00"
                        ],
                        "temperature_2m": [20.0, 21.0, 19.5, 20.5, 20.0, 19.0, 20.0]
                    }
                },
                "air_quality": {
                    "hourly": {
                        "time": [
                            "2024-01-01T14:00", "2024-01-02T14:00",
                            "2024-01-03T14:00", "2024-01-04T14:00",
                            "2024-01-05T14:00", "2024-01-06T14:00",
                            "2024-01-07T14:00"
                        ],
                        "pm2_5": [30.0, 32.0, 28.0, 31.0, 29.0, 30.0, 30.0]
                    }
                }
            },
            {
                "district_name": "Dhaka",
                "forecast": {
                    "hourly": {
                        "time": [
                            "2024-01-01T14:00", "2024-01-02T14:00",
                            "2024-01-03T14:00", "2024-01-04T14:00",
                            "2024-01-05T14:00", "2024-01-06T14:00",
                            "2024-01-07T14:00"
                        ],
                        "temperature_2m": [28.0, 29.0, 27.5, 28.5, 28.0, 27.0, 28.0]
                    }
                },
                "air_quality": {
                    "hourly": {
                        "time": [
                            "2024-01-01T14:00", "2024-01-02T14:00",
                            "2024-01-03T14:00", "2024-01-04T14:00",
                            "2024-01-05T14:00", "2024-01-06T14:00",
                            "2024-01-07T14:00"
                        ],
                        "pm2_5": [120.0, 125.0, 118.0, 122.0, 121.0, 119.0, 120.0]
                    }
                }
            }
        ]

    def test_avg_at_2pm_calculation(self):
        times = ["2024-01-01T14:00", "2024-01-02T14:00", "2024-01-03T14:00"]
        values = [20.0, 22.0, 21.0]

        avg = self.service._avg_at_2pm(times, values)

        self.assertEqual(avg, 21.0)

    def test_avg_at_2pm_filters_non_2pm(self):
        times = ["2024-01-01T10:00", "2024-01-01T14:00", "2024-01-01T18:00"]
        values = [15.0, 20.0, 25.0]

        avg = self.service._avg_at_2pm(times, values)

        self.assertEqual(avg, 20.0)

    def test_avg_at_2pm_with_none_values(self):
        times = ["2024-01-01T14:00", "2024-01-02T14:00", "2024-01-03T14:00"]
        values = [20.0, None, 22.0]

        avg = self.service._avg_at_2pm(times, values)

        self.assertEqual(avg, 21.0)

    def test_extract_metrics_success(self):
        weather = self.mock_weather_data[0]

        metrics = self.service._extract_metrics(weather)

        self.assertIsNotNone(metrics)
        self.assertIn("avg_temp", metrics)
        self.assertIn("avg_pm25", metrics)
        self.assertEqual(metrics["avg_temp"], 20.0)

    def test_extract_metrics_missing_data(self):
        weather = {"district_name": "Test", "forecast": None, "air_quality": None}

        metrics = self.service._extract_metrics(weather)

        self.assertIsNone(metrics)

    @patch.object(BestDistrictsService, '_extract_metrics')
    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_sorting(self, mock_district_service, mock_weather_service, mock_extract):
        mock_district_service.return_value.get_all_districts.return_value = [
            {"name": "Dhaka"}, {"name": "Sylhet"}
        ]

        mock_weather_service.return_value.batch_get_weather.return_value = self.mock_weather_data

        def extract_side_effect(weather):
            district_name = weather.get("district_name", "")
            if district_name == "Dhaka":
                return {"avg_temp": 20.0, "avg_pm25": 30.0}
            elif district_name == "Sylhet":
                return {"avg_temp": 28.0, "avg_pm25": 120.0}
            return {"avg_temp": 20.0, "avg_pm25": 30.0}

        mock_extract.side_effect = extract_side_effect

        service = BestDistrictsService()

        results = service.get_best_districts(limit=2)

        self.assertEqual(results[0]["district"], "Dhaka")
        self.assertEqual(results[1]["district"], "Sylhet")

    @patch.object(BestDistrictsService, '_extract_metrics')
    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_tie_breaking(self, mock_district_service, mock_weather_service, mock_extract):
        # Mock the districts and weather
        mock_district_service.return_value.get_all_districts.return_value = [
            {"name": "District1"}, {"name": "District2"}
        ]
        mock_weather_service.return_value.batch_get_weather.return_value = [
            {"district_name": "District1"}, {"district_name": "District2"}
        ]

        # Mock tie-breaking metrics
        def extract_side_effect(weather):
            district_name = weather.get("district_name", "")
            if district_name == "District1":
                return {"avg_temp": 25.0, "avg_pm25": 50.0}
            elif district_name == "District2":
                return {"avg_temp": 25.0, "avg_pm25": 60.0}
            return {"avg_temp": 25.0, "avg_pm25": 50.0}

        mock_extract.side_effect = extract_side_effect

        # ✅ instantiate AFTER patching
        service = BestDistrictsService()

        results = service.get_best_districts(limit=2)
        self.assertEqual(results[0]["district"], "District1")
