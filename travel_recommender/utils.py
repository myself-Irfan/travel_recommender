import json
import os
from typing import List
from django.core.exceptions import ImproperlyConfigured
from urllib.parse import urljoin, quote_plus


def get_env_or_raise(key: str) -> str:
    value = os.getenv(key)
    if value is None or value.strip() == "":
        raise ImproperlyConfigured(
            f"Environment variable '{key}' is required but not set."
        )
    return value.strip()

def get_env_as_list(key: str, *, lower: bool = True) -> List[str]:
    value = get_env_or_raise(key)
    items = [v.strip() for v in value.split(",") if v.strip()]

    if lower:
        items = [v.lower() for v in items]

    return items


def str_to_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("true", "1", "yes"):
        return True
    if normalized in ("false", "0", "no"):
        return False

    raise ImproperlyConfigured(
        f"Invalid boolean value '{value}'. Expected one of: true, false, 1, 0, yes, no."
    )

def parse_json_or_string(input_data):
    if isinstance(input_data, str):
        try:
            data = json.loads(input_data)
        except ValueError as e:
            data = input_data
    else:
        data = input_data

    return data

def multi_urljoin(*parts) -> str:
    url = urljoin(
        parts[0].strip("/") + "/",
        "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:])
    )
    return url