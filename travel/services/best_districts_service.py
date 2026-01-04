from typing import List, Dict, Any, Optional
from structlog import get_logger

from travel.services.district_service import DistrictService
from travel.services.weather_service import WeatherService

logger = get_logger(__name__)


class BestDistrictsService:
    DEFAULT_LIMIT = 10

    def __init__(self):
        self.district_service = DistrictService()
        self.weather_service = WeatherService()

    def _avg_at_2pm(self, times: List[str], values: List[Optional[float]]) -> Optional[float]:
        collected = []

        for i, time in enumerate(times):
            if time.endswith("T14:00") and i < len(values):
                value = values[i]
                if value is not None:
                    collected.append(value)

        if not collected:
            return None

        return sum(collected) / len(collected)

    def _extract_metrics(self, weather: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        forecast = weather.get("forecast")
        air = weather.get("air_quality")

        if not forecast or not air:
            return None

        # Temperature
        f_hourly = forecast.get("hourly", {})
        avg_temp = self._avg_at_2pm(
            f_hourly.get("time", []),
            f_hourly.get("temperature_2m", []),
        )

        # PM2.5
        a_hourly = air.get("hourly", {})
        avg_pm25 = self._avg_at_2pm(
            a_hourly.get("time", []),
            a_hourly.get("pm2_5", []),
        )

        if avg_temp is None or avg_pm25 is None:
            return None

        return {
            "avg_temp": avg_temp,
            "avg_pm25": avg_pm25,
        }

    def get_best_districts(self, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
        districts = self.district_service.get_all_districts()
        weather_data = self.weather_service.batch_get_weather(districts)

        results = []

        for weather in weather_data:
            metrics = self._extract_metrics(weather)
            if not metrics:
                continue

            results.append({
                "district": weather["district_name"],
                "avg_temp": round(metrics["avg_temp"], 2),
                "avg_pm25": round(metrics["avg_pm25"], 2),
            })

        # 🔥 CORE REQUIREMENT SORT
        results.sort(key=lambda x: (x["avg_temp"], x["avg_pm25"]))

        logger.info("best_districts_computed", total=len(results))

        return results[:limit]
