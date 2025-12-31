from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from structlog import get_logger

from travel.services.weather_service import WeatherService
from travel.services.district_service import DistrictService

logger = get_logger(__name__)

class TravelRecommendationAPIView(APIView):
    api_name = "recommend"

    def post(self, request):
        try:
            # Extract input data
            current_lat = request.data.get("current_lat")
            current_lon = request.data.get("current_lon")
            destination_name = request.data.get("destination_district")
            travel_date = request.data.get("travel_date")  # if needed later

            if not all([current_lat, current_lon, destination_name]):
                return Response(
                    {"error": "current_lat, current_lon, and destination_district are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            district_service = DistrictService()
            weather_service = WeatherService()

            # Create a pseudo-district for current location
            current_district = {
                "name": "current_location",
                "lat": current_lat,
                "long": current_lon
            }

            current_weather = weather_service.get_weather(current_district)

            # Find the destination district by name
            dest_district = district_service.get_district_by_name(destination_name)
            if not dest_district:
                return Response(
                    {"error": f"Destination district '{destination_name}' not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            dest_weather = weather_service.get_weather(dest_district)

            # Safely compute PM2.5 difference
            avg_temp_diff = None
            pm25_diff = None

            if current_weather.get("avg_temp") is not None and dest_weather.get("avg_temp") is not None:
                avg_temp_diff = dest_weather["avg_temp"] - current_weather["avg_temp"]

            if current_weather.get("avg_pm25") is not None and dest_weather.get("avg_pm25") is not None:
                pm25_diff = dest_weather["avg_pm25"] - current_weather["avg_pm25"]

            response_data = {
                "current_weather": current_weather,
                "destination_weather": dest_weather,
                "avg_temp_diff": avg_temp_diff,
                "pm25_diff": pm25_diff,
                "travel_date": travel_date
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("travel_recommendation_error", error=str(e))
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

