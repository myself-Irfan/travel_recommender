from structlog import get_logger
from typing import Dict, Any, List
from django.core.cache import cache
from django.conf import settings

from travel_recommender.services.external_api_request_response import ExternalApiService

logger = get_logger(__name__)

class DistrictService:
    CACHE_KEY = "districts"

    def __init__(self):
        self.api_service = ExternalApiService()
        self.base_url = settings.DISTRICTS_JSON_URL
        self.cache_ttl = settings.DISTRICTS_CACHE_TTL

    def get_all_districts(self) -> List[Dict[str, Any]]:
        cached = cache.get(self.CACHE_KEY)
        if cached:
            logger.info("districts_cache_hit", key=self.CACHE_KEY)
            return cached

        logger.info("fetching_districts_from_api", url=self.base_url)
        response = self.api_service.handle_get(url=self.base_url)

        if response.status_code == 200:
            districts = response.data.get("districts", []) if isinstance(response.data, dict) else []
            cache.set(self.CACHE_KEY, districts, timeout=self.cache_ttl)
            logger.info("districts_cached", key=self.CACHE_KEY, count=len(districts))
            return districts
        else:
            logger.error(
                "failed_fetching_districts",
                url=self.base_url,
                status=response.status_code,
                error=response.actual_error
            )
            return []

    def get_district_by_name(self, name: str) -> Dict[str, Any]:
        districts = self.get_all_districts()
        for district in districts:
            if district.get("name").lower() == name.lower():
                logger.info("district_found", name=name)
                return district

        logger.warning("district_not_found", name=name)
        return {}