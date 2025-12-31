from typing import Dict, Any

from django.conf import settings


class DataMasker:
    @staticmethod
    def mask_headers(headers: Dict[str, str]) -> Dict[str, str]:
        safe_headers = {}
        for key, value in headers.items():
            if key.lower() in settings.SENSITIVE_HEADERS:
                safe_headers[key] = "*" * len(value) if value else "*"
            else:
                safe_headers[key] = value

        return safe_headers

    @classmethod
    def mask_sensitive(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {key: cls._mask_value(key, value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls.mask_sensitive(item) for item in data]
        return data

    @staticmethod
    def _mask_value(key: str, value: Any) -> Any:
        if isinstance(key, str) and key.lower() in settings.SENSITIVE_KEYS and isinstance(value, str):
            return "*" * len(value)
        if isinstance(value, (dict, list)):
            return DataMasker.mask_sensitive(value)
        return value
