from celery import shared_task
from structlog import get_logger
from travel.services.district_service import DistrictService


logger = get_logger(__name__)

@shared_task(name="travel.tasks.update_districts_task")
def update_districts_task():
    logger.info("update_districts_task_started")

    try:
        service = DistrictService()
        districts = service.get_all_districts()
        logger.info("update_districts_task_completed", count=len(districts))
        return {"status": "success", "count": len(districts)}
    except Exception as e:
        logger.error("update_districts_task_failed", error=str(e), exc_info=True)
        raise
