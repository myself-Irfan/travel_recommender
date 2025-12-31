from django.urls import path

from travel.views.best_district_view import BestDistrictsAPIView
from travel.views.recommend import TravelRecommendationAPIView


urlpatterns = [
    path("best-districts/", BestDistrictsAPIView.as_view(), name=BestDistrictsAPIView.api_name),
    path("recommend/", TravelRecommendationAPIView.as_view(), name=TravelRecommendationAPIView.api_name),
]
