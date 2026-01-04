from celery import shared_task
from structlog import get_logger
from travel.services.weather_service import WeatherService
from travel.services.district_service import DistrictService

logger = get_logger(__name__)

@shared_task(name="travel.tasks.update_weather_task")
def update_weather_task():
    logger.info("update_weather_task_started")

    try:
        district_service = DistrictService()
        weather_service = WeatherService()

        districts = district_service.get_all_districts()
        logger.info("weather_update_fetching_districts", total=len(districts))

        updated_count = 0

        for district in districts:
            data = weather_service.get_weather_for_district(district=district)
            if data:
                updated_count += 1

        logger.info("update_weather_task_completed", updated=updated_count, total=len(districts))

        return {"status": "success", "updated": updated_count, "total": len(districts)}
    except Exception as e:
        logger.error("update_weather_task_failed", error=str(e), exc_info=True)
        raise
