from typing import Dict, Any
from datetime import date
from structlog import get_logger

from travel.services.district_service import DistrictService
from travel.services.weather_service import WeatherService

logger = get_logger(__name__)


class RecommendService:
    def __init__(self):
        self.district_service = DistrictService()
        self.weather_service = WeatherService()

    def _get_value_at_2pm_on_date(self, times: list, values: list, target_date: date) -> float | None:
        """
        Get value at 2 PM on a specific date.

        Args:
            times: List of ISO datetime strings (e.g., "2024-01-15T14:00")
            values: Corresponding values
            target_date: Target date object

        Returns:
            Value at 2 PM on target date, or None if not found
        """
        # Format: "YYYY-MM-DDTHH:MM"
        target_datetime = f"{target_date.isoformat()}T14:00"

        for t, v in zip(times, values):
            if t == target_datetime and v is not None:
                return v

        logger.warning("value_not_found_for_date", target=target_datetime)
        return None

    def _fetch_metrics_for_date(
            self,
            district_name: str,
            lat: float,
            lon: float,
            travel_date: date
    ) -> dict | None:
        weather = self.weather_service.get_weather_for_district(
            district={"name": district_name, "lat": lat, "long": lon}
        )

        if not weather:
            logger.warning("weather_data_unavailable", location=district_name)
            return None

        forecast = weather.get("forecast", {}).get("hourly", {})
        temp = self._get_value_at_2pm_on_date(
            forecast.get("time", []),
            forecast.get("temperature_2m", []),
            travel_date
        )

        air = weather.get("air_quality", {}).get("hourly", {})
        pm25 = self._get_value_at_2pm_on_date(
            air.get("time", []),
            air.get("pm2_5", []),
            travel_date
        )

        if temp is None or pm25 is None:
            logger.warning(
                "incomplete_weather_data_for_date",
                location=district_name,
                date=travel_date.isoformat(),
                has_temp=temp is not None,
                has_pm25=pm25 is not None
            )
            return None

        return {
            "temp": round(temp, 1),
            "pm25": round(pm25, 1)
        }

    def recommend(
            self,
            current_lat: float,
            current_lon: float,
            destination_name: str,
            travel_date: date
    ) -> Dict[str, Any]:
        logger.info(
            "recommendation_request_started",
            destination=destination_name,
            travel_date=travel_date.isoformat()
        )

        destination = self.district_service.get_district_by_name(destination_name)
        if not destination:
            logger.warning("destination_not_found", name=destination_name)
            return {
                "recommendation": "Not Recommended",
                "reason": f"Destination '{destination_name}' not found in our database."
            }

        current_metrics = self._fetch_metrics_for_date(
            "Current Location",
            current_lat,
            current_lon,
            travel_date
        )
        if not current_metrics:
            return {
                "recommendation": "Not Recommended",
                "reason": f"Weather data unavailable for your current location on {travel_date.strftime('%B %d, %Y')}."
            }

        dest_metrics = self._fetch_metrics_for_date(
            destination["name"],
            float(destination["lat"]),
            float(destination["long"]),
            travel_date
        )
        if not dest_metrics:
            return {
                "recommendation": "Not Recommended",
                "reason": f"Weather data unavailable for {destination_name} on {travel_date.strftime('%B %d, %Y')}."
            }

        temp_diff = dest_metrics["temp"] - current_metrics["temp"]
        pm25_diff = dest_metrics["pm25"] - current_metrics["pm25"]

        logger.info(
            "recommendation_metrics_computed",
            destination=destination_name,
            temp_diff=temp_diff,
            pm25_diff=pm25_diff
        )

        is_cooler = temp_diff < 0
        is_cleaner = pm25_diff < 0

        if is_cooler and is_cleaner:
            reason = (
                f"Your destination is {abs(temp_diff):.1f}°C cooler "
                f"and has significantly better air quality (PM2.5: {dest_metrics['pm25']} vs {current_metrics['pm25']}). "
                f"Enjoy your trip!"
            )
            recommendation = "Recommended"

        elif not is_cooler and not is_cleaner:
            temp_str = f"{abs(temp_diff):.1f}°C hotter" if temp_diff > 0 else "same temperature"
            reason = (
                f"Your destination is {temp_str} "
                f"and has worse air quality than your current location. "
                f"It's better to stay where you are."
            )
            recommendation = "Not Recommended"

        else:
            if is_cooler:
                temp_str = f"{abs(temp_diff):.1f}°C cooler"
                air_str = f"worse air quality (PM2.5: {dest_metrics['pm25']} vs {current_metrics['pm25']})"
            else:
                temp_str = f"{abs(temp_diff):.1f}°C hotter" if temp_diff > 0 else "similar temperature"
                air_str = f"better air quality (PM2.5: {dest_metrics['pm25']} vs {current_metrics['pm25']})"

            reason = (
                f"Your destination is {temp_str} but has {air_str}. "
                f"Consider your priorities when deciding."
            )
            recommendation = "Recommended" if is_cleaner else "Not Recommended"

        logger.info(
            "recommendation_completed",
            destination=destination_name,
            recommendation=recommendation
        )

        return {
            "recommendation": recommendation,
            "reason": reason,
            "travel_date": travel_date.isoformat(),
            "current_location": {
                "temperature": current_metrics["temp"],
                "pm25": current_metrics["pm25"]
            },
            "destination": {
                "name": destination["name"],
                "temperature": dest_metrics["temp"],
                "pm25": dest_metrics["pm25"]
            }
        }