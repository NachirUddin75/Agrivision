from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework import status
from soil.models import SoilAnalysis
from .recommender import recommend, care_plan
from .gemini_service import generate_advice, generate_ai_recommendations, GeminiUnavailable
from .weather_service import fetch_weather, WeatherUnavailable


def owned_soil(request):
    soil_id = request.query_params.get("soil_id") or request.data.get("soil_id")
    owned = SoilAnalysis.objects.filter(user=request.user)
    if soil_id:
        try:
            return owned.get(pk=soil_id)
        except (SoilAnalysis.DoesNotExist, ValueError, TypeError):
            raise NotFound("Soil analysis not found.")
    return owned.order_by("-created_at").first()


def _resolve_recommendations(analysis, force_refresh=False):
    try:
        ai_result = generate_ai_recommendations(analysis, force_refresh=force_refresh)
        return (
            ai_result["crops"],
            f"Google Gemini AI ({ai_result['model']})",
            True,
            "AI-generated crop recommendations based on your soil profile and location; verify locally.",
        )
    except GeminiUnavailable:
        return (
            recommend(analysis),
            "Illustrative rule-based suitability scoring (not trained ML)",
            False,
            "Scores are illustrative matches, not probabilities of yield or professional recommendations.",
        )


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analysis = owned_soil(request)
        if analysis is None:
            return Response({"analysis": None, "recommendations": [], "message": "Create a soil analysis first."})

        force_refresh = request.query_params.get("refresh") == "1"
        results, method, ai_powered, disclaimer = _resolve_recommendations(analysis, force_refresh=force_refresh)

        selected = request.query_params.get("crop", "")
        crop = next((c for c in results if c["name"].lower() == selected.lower()), None) if selected else (results[0] if results else None)
        if selected and crop is None:
            raise ValidationError({"crop": "Unknown crop name."})

        selected_care_plan = (
            crop.get("care_plan")
            if ai_powered and crop and isinstance(crop.get("care_plan"), dict)
            else care_plan(analysis, crop)
        )

        clean_results = [
            {k: v for k, v in item.items() if k != "care_plan"}
            for item in results
        ]

        return Response({
            "analysis": {
                "id": analysis.id,
                "soil_type": analysis.soil_type,
                "soil_ph": analysis.soil_ph,
                "location": analysis.location,
                "created_at": analysis.created_at,
            },
            "ai_powered": ai_powered,
            "method": method,
            "recommendations": clean_results,
            "care_plan": selected_care_plan,
            "disclaimer": disclaimer,
        })


class GeminiAdviceView(APIView):
    """POST only so repeated page loads do not automatically incur Gemini usage."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic = request.data.get("topic")
        if topic not in ("soil", "crops", "care", "weather"):
            raise ValidationError({"topic": "Choose soil, crops, care or weather."})
        analysis = owned_soil(request)
        if analysis is None:
            raise NotFound("Create a soil analysis first.")

        recommendations, _, _, _ = _resolve_recommendations(analysis)
        selected = str(request.data.get("crop") or "").strip()
        crop = None
        if topic == "care":
            crop = next((c for c in recommendations if c["name"].lower() == selected.lower()), None)
            if crop is None:
                raise ValidationError({"crop": "Select a valid crop."})
        try:
            weather = None
            if topic == "weather":
                city = str(request.data.get("city") or "").strip()
                if not city:
                    raise ValidationError({"city": "Enter a city to use weather-guided AI advice."})
                try:
                    weather = fetch_weather(city)
                except ValueError as exc:
                    raise ValidationError({"city": str(exc)}) from exc
                except WeatherUnavailable as exc:
                    return Response({"detail": str(exc), "ai_available": False}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            guidance = generate_advice(topic, analysis, crop, recommendations, weather=weather)
        except GeminiUnavailable as exc:
            return Response({"detail": str(exc), "ai_available": False}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"ai_available": True, "topic": topic, "guidance": guidance})