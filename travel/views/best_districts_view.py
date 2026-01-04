from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from structlog import get_logger

from travel.serializers.best_districts_serializer import BestDistrictsSerializer
from travel.services.best_districts_service import BestDistrictsService

logger = get_logger(__name__)


class BestDistrictsAPIView(APIView):
    api_name = "best_districts"

    def get(self, request):
        serializer = BestDistrictsSerializer(data=request.query_params)

        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        limit = serializer.validated_data["limit"]

        service = BestDistrictsService()
        result = service.get_best_districts(limit=limit)

        return Response(
            {
                "count": len(result),
                "results": result
            },
            status=status.HTTP_200_OK
        )