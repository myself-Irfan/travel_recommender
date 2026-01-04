from rest_framework import status
from structlog import get_logger
from typing import Dict, Any, List, Optional
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

    @staticmethod
    def _is_valid_response(response) -> bool:
        return response.status_code == status.HTTP_200_OK and isinstance(response.data, dict)

    @staticmethod
    def _normalize_name(value: Optional[str]) -> str:
        return (value or "").strip().lower()

    @staticmethod
    def __index_districts(districts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        indexed = {}

        for district in districts:
            name = DistrictService._normalize_name(district.get("name"))
            if not name:
                continue
            indexed[name] = district

        return indexed

    def _get_indexed_districts(self) -> Dict[str, Dict[str, Any]]:
        cached = cache.get(self.CACHE_KEY)

        if cached is not None:
            logger.info("districts_cache_hit", key=self.CACHE_KEY)
            return cached

        logger.info("fetching_districts_from_api", url=self.base_url)
        response = self.api_service.handle_get(url=self.base_url)

        if not self._is_valid_response(response):
            logger.error(
                "failed_fetching_districts",
                url=self.base_url,
                status=response.status_code,
                error=response.actual_error,
            )
            return {}

        indexed = self.__index_districts(response.data.get("districts", []))
        cache.set(self.CACHE_KEY, indexed, timeout=self.cache_ttl)

        logger.info(
            "districts_cached_indexed",
            key=self.CACHE_KEY,
            count=len(indexed),
        )
        return indexed

    def get_all_districts(self) -> List[Dict[str, Any]]:
        return list(self._get_indexed_districts().values())

    def get_district_by_name(self, name: str) -> Dict[str, Any] | None:
        normalized_name = self._normalize_name(name)
        indexed = self._get_indexed_districts()

        district = indexed.get(normalized_name)
        if district:
            logger.info("district_found", name=normalized_name)
            return district

        logger.warning("district_not_found", name=normalized_name)
        return None