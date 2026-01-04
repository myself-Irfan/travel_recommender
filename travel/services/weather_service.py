from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional

from rest_framework import status
from structlog import get_logger
from django.core.cache import cache
from django.conf import settings

from travel_recommender.services.external_api_request_response import ExternalApiService
from travel_recommender.utils import multi_urljoin

logger = get_logger(__name__)


class WeatherService:
    CACHE_KEY_TEMPLATE = "weather:{district_name}"

    def __init__(self):
        self.api_service = ExternalApiService()
        self.forecast_base_url = settings.OPEN_METEO_BASE_URL
        self.air_quality_base_url = settings.OPEN_METEO_AIR_QUALITY_BASE_URL
        self.cache_ttl = settings.WEATHER_CACHE_TTL

    def get_forecast(self, *, district_name: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        url = multi_urljoin(self.forecast_base_url, "forecast")
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "timezone": "Asia/Dhaka",
            "forecast_days": 7,
        }

        logger.info("fetching_forecast_from_api", district=district_name)
        response = self.api_service.handle_get(url=url, params=params)

        if response.status_code != status.HTTP_200_OK or not isinstance(response.data, dict):
            logger.error("failed_fetching_forecast", district=district_name, status=response.status_code)
            return None

        return response.data

    def get_air_quality(self, *, district_name: str, lat: float, lon: float) -> Dict[str, Any] | None:
        url = multi_urljoin(self.air_quality_base_url, "air-quality")
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "pm2_5,pm10",
            "timezone": "Asia/Dhaka",
            "forecast_days": 7,
        }

        logger.info("fetching_air_quality_from_api", district=district_name)
        response = self.api_service.handle_get(url=url, params=params)

        if response.status_code != status.HTTP_200_OK or not isinstance(response.data, dict):
            logger.error("failed_fetching_air_quality", district=district_name, status=response.status_code)
            return None

        return response.data

    def get_weather_for_district(self, *, district: Dict[str, Any]) -> Dict[str, Any] | None:
        district_name = district.get("name")
        lat, lon = district.get("lat"), district.get("long")
        if not district_name or lat is None or lon is None:
            logger.warning("district_missing_data", district=district_name)
            return None

        cache_key = self.CACHE_KEY_TEMPLATE.format(district_name=district_name)

        cached = cache.get(cache_key)
        if cached is not None:
            logger.info("weather_cache_hit", district=district_name)
            return cached

        forecast = self.get_forecast(district_name=district_name, lat=float(lat), lon=float(lon))
        air_quality = self.get_air_quality(district_name=district_name, lat=float(lat), lon=float(lon))

        if forecast is None and air_quality is None:
            logger.warning("no_weather_data_fetched", district=district_name)
            return None

        data = {
            "district_name": district_name,
            "forecast": forecast,
            "air_quality": air_quality,
        }

        cache.set(cache_key, data, timeout=self.cache_ttl)
        logger.info("weather_cached", district=district_name)

        return data

    def batch_get_weather(self, districts: List[Dict[str, Any]], max_workers: int = 8) -> List[Dict[str, Any]]:
        results = []

        def fetch_single(d):
            try:
                return self.get_weather_for_district(district=d)
            except Exception as e:
                logger.error("weather_fetch_exception", district=d.get("name"), error=str(e))
                return None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_district = {executor.submit(fetch_single, d): d for d in districts}

            for future in as_completed(future_to_district):
                res = future.result()
                if res:
                    results.append(res)

        logger.info("batch_weather_fetch_completed", total=len(districts), successful=len(results))
        return results
