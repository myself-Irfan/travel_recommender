from django.urls import path

from travel.views.district_list_view import DistrictListView
from travel.views.district_detail_view import DistrictDetailView


urlpatterns = [
    path("districts/", DistrictListView.as_view(), name=DistrictListView.api_name),
    path("districts/<str:name>/", DistrictDetailView.as_view(), name=DistrictDetailView.api_name),
]
