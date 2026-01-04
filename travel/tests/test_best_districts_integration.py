from django.test import TestCase
from django.core.cache import cache
from travel.services.best_districts_service import BestDistrictsService
import responses
from django.conf import settings


class BestDistrictsIntegrationTests(TestCase):
    """Integration tests that test the full flow without mocking"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @responses.activate
    def test_full_flow_with_real_api_calls(self):
        """Test the complete flow with mocked external API responses"""
        # Mock districts API
        responses.add(
            responses.GET,
            settings.DISTRICTS_JSON_URL,
            json={
                "districts": [
                    {"name": "Dhaka", "lat": 23.8103, "long": 90.4125},
                    {"name": "Chittagong", "lat": 22.3569, "long": 91.7832},
                ]
            },
            status=200
        )

        responses.add(
            responses.GET,
            f"{settings.OPEN_METEO_BASE_URL}/forecast",
            json={
                "hourly": {
                    "time": ["2026-01-02T14:00", "2026-01-03T14:00"],
                    "temperature_2m": [25.0, 26.0],
                    "pm2_5": [50.0, 55.0]
                }
            },
            status=200
        )

        # Mock weather API for Chittagong
        responses.add(
            responses.GET,
            f"{settings.OPEN_METEO_BASE_URL}/forecast",
            json={
                "hourly": {
                    "time": ["2026-01-02T14:00", "2026-01-03T14:00"],
                    "temperature_2m": [27.0, 28.0],
                    "pm2_5": [60.0, 65.0]
                }
            },
            status=200
        )

        service = BestDistrictsService()
        results = service.get_best_districts(limit=2)

        self.assertEqual(len(results), 2)
        # Dhaka should be first (cooler)
        self.assertEqual(results[0]['district'], 'Dhaka')