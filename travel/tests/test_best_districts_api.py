from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase


class BestDistrictsAPIViewTests(APITestCase):

    def setUp(self):
        cache.clear()
        self.url = reverse('best_districts')

    def tearDown(self):
        cache.clear()

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_default_limit(self, mock_district_service, mock_weather_service):
        """Test GET request with default limit of 10"""
        # Mock district data
        mock_districts = [
            {"name": f"District{i}", "lat": 23.0 + i, "long": 90.0 + i}
            for i in range(15)
        ]

        # Mock weather data
        mock_weather_data = [
            {
                "location": f"District{i}",
                "avg_temp": 25.0 + i,
                "avg_pm25": 50.0 + i
            }
            for i in range(15)
        ]

        mock_district_service.return_value.get_all_districts.return_value = mock_districts
        mock_weather_service.return_value.batch_get_weather.return_value = mock_weather_data

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 10)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('results', response.data)

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_custom_limit(self, mock_district_service, mock_weather_service):
        """Test GET request with custom limit"""
        mock_districts = [
            {"name": f"District{i}", "lat": 23.0 + i, "long": 90.0 + i}
            for i in range(10)
        ]

        mock_weather_data = [
            {
                "location": f"District{i}",
                "avg_temp": 25.0 + i,
                "avg_pm25": 50.0 + i
            }
            for i in range(10)
        ]

        mock_district_service.return_value.get_all_districts.return_value = mock_districts
        mock_weather_service.return_value.batch_get_weather.return_value = mock_weather_data

        response = self.client.get(self.url, {'limit': 5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['results']), 5)

    def test_get_best_districts_invalid_limit_negative(self):
        """Test GET request with negative limit"""
        response = self.client.get(self.url, {'limit': -1})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_best_districts_invalid_limit_exceeds_max(self):
        """Test GET request with limit exceeding maximum"""
        response = self.client.get(self.url, {'limit': 100})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_best_districts_invalid_limit_not_integer(self):
        """Test GET request with non-integer limit"""
        response = self.client.get(self.url, {'limit': 'abc'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_get_best_districts_limit_zero(self):
        """Test GET request with limit of 0"""
        response = self.client.get(self.url, {'limit': 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_sorted_by_temp_then_pm25(self, mock_district_service, mock_weather_service):
        """Test that results are sorted by temperature first, then PM2.5"""
        mock_districts = [
            {"name": "District1", "lat": 23.0, "long": 90.0},
            {"name": "District2", "lat": 24.0, "long": 91.0},
            {"name": "District3", "lat": 25.0, "long": 92.0},
        ]

        # District2 has same temp as District1 but better air quality
        mock_weather_data = [
            {"location": "District1", "avg_temp": 25.0, "avg_pm25": 60.0},
            {"location": "District2", "avg_temp": 25.0, "avg_pm25": 50.0},
            {"location": "District3", "avg_temp": 30.0, "avg_pm25": 40.0},
        ]

        mock_district_service.return_value.get_all_districts.return_value = mock_districts
        mock_weather_service.return_value.batch_get_weather.return_value = mock_weather_data

        response = self.client.get(self.url, {'limit': 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']

        # First should be District2 (temp=25, pm25=50)
        self.assertEqual(results[0]['district'], 'District2')
        # Second should be District1 (temp=25, pm25=60)
        self.assertEqual(results[1]['district'], 'District1')
        # Third should be District3 (temp=30, pm25=40)
        self.assertEqual(results[2]['district'], 'District3')

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_cache_hit(self, mock_district_service, mock_weather_service):
        """Test that cached results are returned on subsequent requests"""
        mock_districts = [
            {"name": "District1", "lat": 23.0, "long": 90.0}
        ]

        mock_weather_data = [
            {"location": "District1", "avg_temp": 25.0, "avg_pm25": 50.0}
        ]

        mock_district_service.return_value.get_all_districts.return_value = mock_districts
        mock_weather_service.return_value.batch_get_weather.return_value = mock_weather_data

        # First request - cache miss
        response1 = self.client.get(self.url, {'limit': 5})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Second request - should hit cache
        response2 = self.client.get(self.url, {'limit': 5})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        # Verify services were only called once (first request)
        mock_district_service.return_value.get_all_districts.assert_called_once()
        mock_weather_service.return_value.batch_get_weather.assert_called_once()

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_filters_incomplete_data(self, mock_district_service, mock_weather_service):
        """Test that districts with missing temperature or PM2.5 data are filtered out"""
        mock_districts = [
            {"name": "District1", "lat": 23.0, "long": 90.0},
            {"name": "District2", "lat": 24.0, "long": 91.0},
            {"name": "District3", "lat": 25.0, "long": 92.0},
        ]

        # District2 has missing PM2.5 data
        mock_weather_data = [
            {"location": "District1", "avg_temp": 25.0, "avg_pm25": 50.0},
            {"location": "District2", "avg_temp": 26.0, "avg_pm25": None},
            {"location": "District3", "avg_temp": 27.0, "avg_pm25": 55.0},
        ]

        mock_district_service.return_value.get_all_districts.return_value = mock_districts
        mock_weather_service.return_value.batch_get_weather.return_value = mock_weather_data

        response = self.client.get(self.url, {'limit': 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return 2 districts (District2 filtered out)
        self.assertEqual(response.data['count'], 2)
        district_names = [r['district'] for r in response.data['results']]
        self.assertNotIn('District2', district_names)

    @patch('travel.services.best_districts_service.WeatherService')
    @patch('travel.services.best_districts_service.DistrictService')
    def test_get_best_districts_empty_results(self, mock_district_service, mock_weather_service):
        """Test handling of empty district list"""
        mock_district_service.return_value.get_all_districts.return_value = []
        mock_weather_service.return_value.batch_get_weather.return_value = []

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['results'], [])