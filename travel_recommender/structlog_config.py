import os
import logging.config
import structlog
from typing import Dict

from travel_recommender.middleware.data_masker import DataMasker
from travel_recommender.utils import get_env_or_raise, get_env_as_list

# ---------------------------------------------------------------------
# ENV
# ---------------------------------------------------------------------
LOG_DIR = get_env_or_raise("LOG_DIR")
LOG_LEVEL = get_env_or_raise("LOG_LEVEL").upper()

DISABLED_FIELDS = get_env_as_list("DISABLED_FIELDS_TO_LOG")
SENSITIVE_KEYS = get_env_as_list("SENSITIVE_KEYS")
SENSITIVE_HEADERS = get_env_as_list("SENSITIVE_HEADERS")

os.makedirs(LOG_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# Structlog processors
# ---------------------------------------------------------------------
def drop_unwanted_fields(_, __, event_dict):
    return {k: v for k, v in event_dict.items() if k not in DISABLED_FIELDS}


def mask_sensitive_data(_, __, event_dict):
    return DataMasker.mask_sensitive(
        event_dict
    )


# ---------------------------------------------------------------------
# Django LOGGING config
# ---------------------------------------------------------------------
def get_logging_config(log_file_name: str) -> Dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(),
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "file": {
                "class": "logging.handlers.WatchedFileHandler",
                "filename": os.path.join(LOG_DIR, log_file_name),
                "formatter": "json",
            },
        },

        "root": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
        },
    }


# ---------------------------------------------------------------------
# Structlog configuration
# ---------------------------------------------------------------------
def configure_logging(log_file_name: str = "app.log"):
    logging.config.dictConfig(get_logging_config(log_file_name))

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,

            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,

            drop_unwanted_fields,
            mask_sensitive_data,

            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.LINENO,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                }
            ),

            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,

            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
