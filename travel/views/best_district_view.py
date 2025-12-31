# travel_recommender/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from travel.services.district_service import DistrictService
from travel.services.weather_service import WeatherService

class BestDistrictsAPIView(APIView):

    api_name = 'best-districts'

    def get(self, request):
        district_service = DistrictService()
        weather_service = WeatherService()

        districts = district_service.get_all_districts()
        all_weather = []

        for district in districts:
            weather = weather_service.get_weather(district)
            if weather:
                all_weather.append(weather)

        # sort by avg temp, then avg PM2.5
        top10 = sorted(all_weather, key=lambda x: (x["avg_temp"], x["avg_pm25"]))[:10]

        return Response(top10, status=status.HTTP_200_OK)
