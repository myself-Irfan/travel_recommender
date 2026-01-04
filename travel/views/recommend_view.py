from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from structlog import get_logger

from travel.serializers.recommend_serializer import RecommendSerializer
from travel.services.recommend_service import RecommendService

logger = get_logger(__name__)


class TravelRecommendationAPIView(APIView):
    api_name = "recommend"

    def get(self, request):
        serializer = RecommendSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        logger.info("recommendation_request_received", data=validated_data)

        service = RecommendService()
        result = service.recommend(**validated_data)

        return Response(result, status=status.HTTP_200_OK)