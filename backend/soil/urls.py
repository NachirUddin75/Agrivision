from django.urls import path

from .views import SoilAnalysisListCreateView


urlpatterns = [
    path(
        "",
        SoilAnalysisListCreateView.as_view(),
        name="soil-analysis",
    ),
]