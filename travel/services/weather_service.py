from structlog import get_logger
from typing import Dict, Any
from django.core.cache import cache
from django.conf import settings

from travel_recommender.services.external_api_request_response import ExternalApiService
from travel_recommender.utils import multi_urljoin

logger = get_logger(__name__)


class WeatherService:
    CACHE_KEY_TEMPLATE = "weather_{district_name}"

    def __init__(self):
        self.api_service = ExternalApiService()
        self.base_url = settings.OPEN_METEO_BASE_URL
        self.cache_ttl = settings.WEATHER_CACHE_TTL

    def get_weather(self, district_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        cache_key = self.CACHE_KEY_TEMPLATE.format(district_name=district_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("weather_cache_hit", key=cache_key)
            return cached

        url = multi_urljoin(self.base_url, "forecast")
        logger.info("fetching_weather_from_api", url=url, district=district_name, params=params)

        response = self.api_service.handle_get(url=url, params=params)
        if response.status_code == 200:
            weather_data = response.data
            cache.set(cache_key, weather_data, timeout=self.cache_ttl)
            logger.info("weather_cached", key=cache_key)
            return weather_data
        else:
            logger.error(
                "failed_fetching_weather",
                url=url,
                district=district_name,
                status=response.status_code,
                error=response.actual_error
            )
            return {}
