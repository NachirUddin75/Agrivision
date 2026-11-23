from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework import status
from .weather_service import fetch_weather, irrigation_note, WeatherUnavailable

class WeatherForecastView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get("city", "")
        try:
            report = fetch_weather(city)
        except ValueError as exc:
            raise ValidationError({"city": str(exc)}) from exc
        except WeatherUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        soil = None
        from .views import owned_soil
        soil = owned_soil(request)
        report = dict(report)
        report["irrigation_guidance"] = irrigation_note(report, soil.moisture if soil else None)
        return Response(report)
