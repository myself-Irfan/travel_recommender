from django.urls import path

from travel.views.best_districts_view import BestDistrictsAPIView
from travel.views.recommend_view import TravelRecommendationAPIView


urlpatterns = [
    path("best-districts/", BestDistrictsAPIView.as_view(), name=BestDistrictsAPIView.api_name),
    path("recommend/", TravelRecommendationAPIView.as_view(), name=TravelRecommendationAPIView.api_name),
]
