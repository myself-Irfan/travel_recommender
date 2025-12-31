from structlog import get_logger
from typing import Dict, Any, Tuple
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

    def get_weather(self, district: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch weather and air quality data for a district.
        Computes avg temp at 2 PM and avg PM2.5 over 7 days.
        """
        district_name = district["name"]
        cache_key = self.CACHE_KEY_TEMPLATE.format(district_name=district_name)
        cached = cache.get(cache_key)
        if cached:
            logger.info("weather_cache_hit", key=cache_key)
            return cached

        url = multi_urljoin(self.base_url, "forecast")
        params = {
            "latitude": float(district["lat"]),
            "longitude": float(district["long"]),
            "hourly": "temperature_2m,pm2_5",
            "timezone": "Asia/Dhaka"
        }

        logger.info("fetching_weather_from_api", url=url, district=district_name)
        response = self.api_service.handle_get(url=url, params=params)

        if response.status_code == 200:
            weather_data = response.data
            avg_temp, avg_pm25 = self.compute_7day_avg(weather_data)
            result = {
                "district": district_name,
                "latitude": float(district["lat"]),
                "longitude": float(district["long"]),
                "avg_temp": avg_temp,
                "avg_pm25": avg_pm25,
                "raw_data": weather_data  # optional, can remove if not needed
            }
            cache.set(cache_key, result, timeout=self.cache_ttl)
            logger.info("weather_cached", key=cache_key)
            return result
        else:
            logger.error(
                "failed_fetching_weather",
                url=url,
                district=district_name,
                status=response.status_code,
                error=response.actual_error
            )
            return {}

    def compute_7day_avg(self, weather_data: Dict[str, Any]) -> Tuple[float, float]:
        """
        Calculate average temperature at 2 PM and average PM2.5 for 7 days.
        """
        hourly = weather_data.get("hourly", {})
        temps = hourly.get("temperature_2m", [])
        pm25s = hourly.get("pm2_5", [])
        times = hourly.get("time", [])

        temp_at_2pm = []
        pm25_at_2pm = []

        for i, time_str in enumerate(times):
            if "14:00" in time_str:  # 2 PM
                if i < len(temps) and temps[i] is not None:
                    temp_at_2pm.append(temps[i])
                if i < len(pm25s) and pm25s[i] is not None:
                    pm25_at_2pm.append(pm25s[i])

        avg_temp = sum(temp_at_2pm) / len(temp_at_2pm) if temp_at_2pm else None
        avg_pm25 = sum(pm25_at_2pm) / len(pm25_at_2pm) if pm25_at_2pm else None

        return avg_temp, avg_pm25
