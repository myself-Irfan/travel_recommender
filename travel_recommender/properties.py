from typing import Any, Optional
from rest_framework import status


class ExtAPIResponseProperty:
    def __init__(self):
        self.data: Any = None
        self.error: Any = None
        self.status_code: int = status.HTTP_200_OK
        self.actual_error: Optional[str] = None
        self.actual_status_code: Optional[int] = None
        self.response: Any = None