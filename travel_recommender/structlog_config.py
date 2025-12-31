import logging
import os
import structlog

from travel_recommender.middleware.data_masker import DataMasker
from travel_recommender.utils import get_env_or_raise

# ---------------------------------------------------------------------
# Required environment variables
# ---------------------------------------------------------------------
LOG_DIR = get_env_or_raise("LOG_DIR")
LOG_LEVEL = get_env_or_raise("LOG_LEVEL")
DISABLED_FIELDS = get_env_or_raise("DISABLED_FIELDS_TO_LOG").split(",")
DISABLED_FIELDS = [f.strip() for f in DISABLED_FIELDS if f.strip()]
DISABLE_STRUCTLOG_DEFAULT_REQUEST_LOGS = get_env_or_raise(
    "DISABLE_STRUCTLOG_DEFAULT_REQUEST_LOGS"
).upper() == "TRUE"

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=LOG_LEVEL.upper())

# ---------------------------------------------------------------------
# Structlog processors
# ---------------------------------------------------------------------
def drop_unwanted_fields(_, __, event_dict):
    return {k: v for k, v in event_dict.items() if k not in DISABLED_FIELDS}

def skip_request_logs(logger, method_name, event_dict):
    event_set = {"request_failed", "request_started", "request_finished"}
    if DISABLE_STRUCTLOG_DEFAULT_REQUEST_LOGS and isinstance(event_dict.get("event"), str) and event_dict.get("event") in event_set:
        raise structlog.DropEvent
    return event_dict

def mask_sensitive_data(_, __, event_dict):
    return DataMasker.mask_sensitive(event_dict)


# ---------------------------------------------------------------------
# Configure structlog
# ---------------------------------------------------------------------
def configure_structlog():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            skip_request_logs,
            structlog.processors.TimeStamper(fmt="iso", utc=False),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            drop_unwanted_fields,
            mask_sensitive_data,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME
                ]
            ),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
