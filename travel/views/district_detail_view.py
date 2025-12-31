from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from travel.services.district_service import DistrictService


class DistrictDetailView(APIView):
    api_name = "district-detail"

    def get(self, request, name: str):
        service = DistrictService()
        district = service.get_district_by_name(name)
        if district:
            return Response(district, status=status.HTTP_200_OK)
        else:
            return Response({"detail": f"District '{name}' not found"}, status=status.HTTP_404_NOT_FOUND)