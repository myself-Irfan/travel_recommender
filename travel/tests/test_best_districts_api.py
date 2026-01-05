from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from datetime import date, timedelta


class BestDistrictsAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('best_districts')

    @patch('travel.views.best_districts_view.BestDistrictsService')
    def test_get_best_districts_success(self, mock_service):
        mock_service.return_value.get_best_districts.return_value = [
            {"district": "Sylhet", "avg_temp": 20.0, "avg_pm25": 30.0},
            {"district": "Rangamati", "avg_temp": 21.0, "avg_pm25": 28.0}
        ]

        response = self.client.get(self.url, {"limit": 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)

    def test_get_best_districts_default_limit(self):
        with patch('travel.views.best_districts_view.BestDistrictsService') as mock_service:
            mock_service.return_value.get_best_districts.return_value = []

            response = self.client.get(self.url)

            mock_service.return_value.get_best_districts.assert_called_with(limit=10)

    def test_get_best_districts_invalid_limit(self):
        response = self.client.get(self.url, {"limit": 0})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_best_districts_limit_too_high(self):
        response = self.client.get(self.url, {"limit": 100})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)