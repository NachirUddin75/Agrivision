from .weather_views import WeatherForecastView
from django.urls import path
from .views import RecommendationView, GeminiAdviceView
urlpatterns = [
    path("weather/", WeatherForecastView.as_view(), name="weather-forecast"),
    path("recommendations/", RecommendationView.as_view(), name="crop-recommendations"),
    path("gemini-advice/", GeminiAdviceView.as_view(), name="gemini-advice"),
]
