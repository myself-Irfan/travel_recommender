import os
from django.core.exceptions import ImproperlyConfigured


def get_env_or_raise(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ImproperlyConfigured(
            f"Environment variable '{key}' is required but not set."
        )
    return value.strip()

def str_to_bool(value: str) -> bool:
    return value.lower() in ("true", "1", "yes")
