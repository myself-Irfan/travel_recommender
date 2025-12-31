import requests
from typing import Optional, Dict, Any, Callable
from django.conf import settings
from structlog import get_logger

from travel_recommender.properties import ExtAPIResponseProperty
from travel_recommender.utils import parse_json_or_string

logger = get_logger(__name__)


class ExternalApiService:
    def __init__(self):
        self.default_headers = {
            "User-Agent": "TravelRecommender/1.0"
        }

    def update_request_headers(self, headers: Optional[Dict]) -> Dict:
        updated_headers = self.default_headers.copy()
        if headers:
            updated_headers.update(headers)
        return updated_headers

    def handle_get(self, url: str, headers: Optional[Dict] = None, success_code: int = 200, params: Dict = None, additional_info: Dict = None) -> ExtAPIResponseProperty:
        headers = self.update_request_headers(headers)
        logger.info(
            "external_api_request_start",
            method="GET",
            url=url,
            headers=headers,
            params=params,
            additional_info=additional_info
        )
        response_obj = self.__make_request(
            method="GET",
            url=url,
            response_method=lambda: requests.get(url, params=params, headers=headers),
            success_code=success_code,
            additional_info=additional_info,
            request_headers=headers,
            request_data=params,
        )
        logger.info(
            "external_api_request_end",
            url=url,
            status_code=response_obj.status_code,
            actual_status_code=response_obj.actual_status_code,
            error=response_obj.error,
        )
        return response_obj

    def __make_request(
            self,
            method: str,
            url: str,
            response_method: Callable,
            success_code: int,
            additional_info: Optional[Dict] = None,
            request_headers: Optional[Dict] = None,
            request_data: Optional[Any] = None,
            is_file: bool = False
    ) -> ExtAPIResponseProperty:
        response_obj = self.__handle_request(
            method=method,
            url=url,
            response_method=response_method,
            success_code=success_code,
            is_file=is_file
        )

        return response_obj

    def __handle_request(
            self,
            method: str,
            url: str,
            response_method: Callable,
            success_code: int,
            is_file: bool
    ) -> ExtAPIResponseProperty:
        response_obj = ExtAPIResponseProperty()
        response_obj.status_code = success_code
        try:
            response = response_method()
            response_obj.response = response
            response_obj.actual_status_code = response.status_code
            response_obj.status_code = response.status_code

            if response.status_code == success_code:
                response_obj.data = parse_json_or_string(response.text) if not is_file else "<File>"
                logger.info(
                    "external_api_success",
                    method=method,
                    url=url,
                    status_code=response.status_code
                )
            else:
                response_obj.error = parse_json_or_string(response.text)
                response_obj.actual_error = response.text
                logger.warning(
                    "external_api_failed",
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    error=response_obj.error
                )

        except requests.exceptions.Timeout as e:
            self.__handle_exception(response_obj, e, 504, url, method)
        except requests.exceptions.RequestException as e:
            self.__handle_exception(response_obj, e, 502, url, method)
        except Exception as e:
            self.__handle_exception(response_obj, e, 502, url, method)

        return response_obj

    @staticmethod
    def __handle_exception(response_obj: ExtAPIResponseProperty, error: Exception, status_code: int, url: str = "", method: str = ""):
        response_text = str(error)
        response_obj.error = response_text
        response_obj.actual_error = response_text
        response_obj.status_code = status_code
        response_obj.actual_status_code = status_code

        logger.error(
            "external_api_exception",
            method=method,
            url=url,
            status_code=status_code,
            error=response_text
        )
