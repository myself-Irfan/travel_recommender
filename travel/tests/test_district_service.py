from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch, MagicMock
from rest_framework import status

from travel.services.district_service import DistrictService


class DistrictServiceTest(TestCase):
    def setUp(self):
        cache.clear()
        self.service = DistrictService()
        self.mock_districts_data = [
            {"id": "1", "name": "Dhaka", "lat": 23.8103, "long": 90.4125},
            {"id": "2", "name": "Chittagong", "lat": 22.3569, "long": 91.7832},
            {"id": "3", "name": "Sylhet", "lat": 24.8949, "long": 91.8687},
        ]

    def tearDown(self):
        cache.clear()

    @patch('travel.services.district_service.cache')
    @patch('travel.services.district_service.ExternalApiService')
    def test_get_all_districts_success(self, mock_api_service, mock_cache):
        mock_cache.get.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = {"districts": self.mock_districts_data}

        mock_api_instance = MagicMock()
        mock_api_instance.handle_get.return_value = mock_response
        mock_api_service.return_value = mock_api_instance

        service = DistrictService()

        districts = service.get_all_districts()

        self.assertEqual(len(districts), len(self.mock_districts_data))
        self.assertIn("name", districts[0])
        self.assertIn("lat", districts[0])

    @patch('travel.services.district_service.ExternalApiService')
    def test_get_district_by_name_found(self, mock_api_service):
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = self.mock_districts_data

        mock_api_service.return_value.handle_get.return_value = mock_response

        district = self.service.get_district_by_name("dhaka")  # lowercase

        self.assertIsNotNone(district)
        self.assertEqual(district["name"], "Dhaka")

    @patch('travel.services.district_service.ExternalApiService')
    def test_get_district_by_name_not_found(self, mock_api_service):
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = self.mock_districts_data

        mock_api_service.return_value.handle_get.return_value = mock_response

        district = self.service.get_district_by_name("NonExistent")

        self.assertIsNone(district)

    @patch('travel.services.district_service.cache')
    @patch('travel.services.district_service.ExternalApiService')
    def test_caching_works(self, mock_api_service, mock_cache):
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.data = {"districts": self.mock_districts_data}

        mock_api_instance = MagicMock()
        mock_api_instance.handle_get.return_value = mock_response
        mock_api_service.return_value = mock_api_instance

        service = DistrictService()

        indexed_districts = {
            service._normalize_name(d["name"]): d
            for d in self.mock_districts_data
        }

        call_count = [0]

        def cache_get_side_effect(key):
            call_count[0] += 1
            if call_count[0] == 1:
                return None
            return indexed_districts

        mock_cache.get.side_effect = cache_get_side_effect
        mock_cache.set.return_value = None

        districts1 = service.get_all_districts()
        districts2 = service.get_all_districts()

        mock_api_instance.handle_get.assert_called_once()

        self.assertEqual(mock_cache.get.call_count, 2)

        mock_cache.set.assert_called_once()

        self.assertEqual(districts1, districts2)

    @patch('travel.services.district_service.cache')
    @patch('travel.services.district_service.ExternalApiService')
    def test_api_failure(self, mock_api_service, mock_cache):
        mock_cache.get.return_value = None

        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_response.data = {}
        mock_response.actual_error = "Internal Server Error"

        mock_api_instance = MagicMock()
        mock_api_instance.handle_get.return_value = mock_response
        mock_api_service.return_value = mock_api_instance

        service = DistrictService()
        districts = service.get_all_districts()

        self.assertEqual(len(districts), 0)
        mock_cache.set.assert_not_called()