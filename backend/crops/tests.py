from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from soil.models import SoilAnalysis
from .recommender import recommend, care_plan


class CropRecommenderTests(SimpleTestCase):
    def test_scores_are_bounded_and_sorted(self):
        soil = SoilAnalysis(soil_type="loamy", soil_ph=6.5, moisture=50)
        result = recommend(soil)
        self.assertTrue(len(result) >= 3)
        scores = [item["score"] for item in result]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 <= score <= 100 for score in scores))
        self.assertIn("not an agronomic prescription", care_plan(soil,result[0])["disclaimer"])

    def test_missing_measurements_are_not_falsely_scored(self):
        soil = SoilAnalysis(soil_type="other")
        self.assertTrue(all(item["score"] is None for item in recommend(soil)))


class CropEndpointTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="farmer", password="pw-strong", email="farmer@example.org")
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
        self.soil = SoilAnalysis.objects.create(user=user, soil_type="loamy", soil_ph=6.4, moisture=50)

    def test_returns_recommendations_and_care(self):
        result = self.client.get("/api/crops/recommendations/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["analysis"]["id"], self.soil.id)
        self.assertTrue(result.data["recommendations"])
        self.assertIn("fertilizer", result.data["care_plan"])
        self.assertIn("not trained ML", result.data["method"])

    def test_unknown_crop_is_rejected(self):
        result = self.client.get("/api/crops/recommendations/?crop=NotACrop")
        self.assertEqual(result.status_code, 400)

from unittest.mock import patch
from .gemini_service import GeminiUnavailable, generate_advice


class GeminiIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="gemini_farmer", password="strong-password", email="ai@example.org")
        self.other_user = get_user_model().objects.create_user(username="another_farmer", password="strong-password", email="other@example.org")
        self.soil = SoilAnalysis.objects.create(user=self.user, soil_type="loamy", soil_ph=6.2, moisture=48)
        self.client = APIClient()
        self.url = "/api/crops/gemini-advice/"

    def sign_in(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")

    def test_login_is_required(self):
        self.assertEqual(self.client.post(self.url, {"topic":"soil"}, format="json").status_code, 401)

    def test_cannot_read_other_users_soil(self):
        self.sign_in(self.other_user)
        self.assertEqual(self.client.post(self.url, {"topic":"soil", "soil_id":self.soil.id}, format="json").status_code, 404)

    def test_rejects_invalid_crop_without_contacting_provider(self):
        self.sign_in(self.user)
        with patch("crops.views.generate_advice") as generator:
            response = self.client.post(self.url, {"topic":"care", "soil_id":self.soil.id, "crop":"Invalid"}, format="json")
        self.assertEqual(response.status_code, 400)
        generator.assert_not_called()

    def test_no_api_key_reports_clear_unavailable_state(self):
        self.sign_in(self.user)
        with patch.dict("os.environ", {"GEMINI_API_KEY":""}):
            response = self.client.post(self.url, {"topic":"crops", "soil_id":self.soil.id}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.data["ai_available"])

    def test_gemini_response_with_mocked_provider(self):
        self.sign_in(self.user)
        with patch.dict("os.environ", {"GEMINI_API_KEY":"test-key", "GEMINI_MODEL":"gemini-2.5-flash"}), patch("crops.gemini_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"candidates":[{"content":{"parts":[{"text":"Check soil moisture before irrigation."}]}}]}
            response = self.client.post(self.url, {"topic":"care", "crop":"Rice", "soil_id":self.soil.id}, format="json")
            self.assertEqual(mock_post.call_count, 1)
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs["headers"]["x-goog-api-key"], "test-key")
            self.assertIn("gemini-2.5-flash:generateContent", args[0])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["guidance"]["text"], "Check soil moisture before irrigation.")

    def test_provider_errors_do_not_leak_key(self):
        self.sign_in(self.user)
        with patch.dict("os.environ", {"GEMINI_API_KEY":"do-not-leak"}), patch("crops.gemini_service.requests.post") as mock_post:
            mock_post.return_value.status_code = 401
            response = self.client.post(self.url, {"topic":"soil", "soil_id":self.soil.id}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("do-not-leak", str(response.data))

from .weather_service import fetch_weather, irrigation_note, WeatherUnavailable


class WeatherIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="weather_farmer", password="testpass", email="weather@example.org")
        self.client = APIClient()

    def sign_in(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(self.user).access_token}")

    def test_weather_requires_login(self):
        self.assertEqual(self.client.get("/api/crops/weather/?city=Howrah").status_code, 401)

    def test_invalid_city_rejected(self):
        self.sign_in()
        self.assertEqual(self.client.get("/api/crops/weather/?city=!").status_code, 400)

    @patch("crops.weather_service.cache.get", return_value=None)
    @patch("crops.weather_service.cache.set")
    @patch("crops.weather_service.requests.get")
    def test_weather_response_and_irrigation(self, mock_get, mock_set, mock_cache):
        self.sign_in()
        geo = {"results": [{"name": "Howrah", "admin1": "West Bengal", "country": "India", "latitude": 22.59, "longitude": 88.31}]}
        forecast = {"timezone": "Asia/Kolkata", "current": {"time": "2026-11-23T12:00", "temperature_2m": 28,
                    "relative_humidity_2m": 65, "precipitation": 0, "weather_code": 1, "wind_speed_10m": 11},
                    "daily": {"time": ["2026-11-23", "2026-11-24"], "weather_code": [1,61],
                    "temperature_2m_max": [29,30], "temperature_2m_min": [20,21],
                    "precipitation_sum": [1,10], "precipitation_probability_max": [10,80]}}
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.side_effect = [type("Response", (), {"raise_for_status": lambda self: None, "json": lambda self: geo})(),
                                type("Response", (), {"raise_for_status": lambda self: None, "json": lambda self: forecast})()]
        response = self.client.get("/api/crops/weather/?city=Howrah")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["location"]["country"], "India")
        self.assertEqual(response.data["forecast"][1]["rain_mm"], 10)
        self.assertIn("Rain is forecast", response.data["irrigation_guidance"])
        self.assertEqual(mock_get.call_count, 2)
        self.assertTrue(mock_set.called)

    def test_ai_weather_requires_soil(self):
        self.sign_in()
        response = self.client.post("/api/crops/gemini-advice/", {"topic": "weather", "city": "Howrah"}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_moisture_guidance(self):
        report = {"forecast": [{"rain_mm": 0, "rain_probability_pct": 10}]}
        self.assertIn("moisture is low", irrigation_note(report, moisture=12))
