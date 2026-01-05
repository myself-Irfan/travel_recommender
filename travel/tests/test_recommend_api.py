from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from datetime import date, timedelta


class TravelRecommendationAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('recommend')
        self.valid_data = {
            "current_lat": 23.8103,
            "current_lon": 90.4125,
            "destination_name": "Sylhet",
            "travel_date": (date.today() + timedelta(days=3)).isoformat()
        }

    @patch('travel.views.recommend_view.RecommendService')
    def test_recommend_success(self, mock_service):
        mock_service.return_value.recommend.return_value = {
            "recommendation": "Recommended",
            "reason": "Your destination is cooler and has better air quality."
        }

        response = self.client.get(self.url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("recommendation", response.data)

    def test_recommend_missing_parameters(self):
        response = self.client.get(self.url, {"current_lat": 23.8103})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_invalid_latitude(self):
        data = self.valid_data.copy()
        data["current_lat"] = 100  # Invalid

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_invalid_longitude(self):
        data = self.valid_data.copy()
        data["current_lon"] = 200

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_past_date(self):
        data = self.valid_data.copy()
        data["travel_date"] = (date.today() - timedelta(days=1)).isoformat()

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recommend_date_too_far(self):
        data = self.valid_data.copy()
        data["travel_date"] = (date.today() + timedelta(days=10)).isoformat()

        response = self.client.get(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)