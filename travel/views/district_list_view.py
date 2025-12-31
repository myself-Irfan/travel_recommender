from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from travel.services.district_service import DistrictService


class DistrictListView(APIView):
    api_name = "district-list"

    def get(self, request):
        service = DistrictService()
        districts = service.get_all_districts()
        if districts:
            return Response(districts, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No districts found"}, status=status.HTTP_404_NOT_FOUND)

