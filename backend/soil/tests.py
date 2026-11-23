from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from .models import SoilAnalysis


class SoilSecurityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.a = User.objects.create_user(username="farmer_a", email="a@example.org", password="strong-pass-1")
        self.b = User.objects.create_user(username="farmer_b", email="b@example.org", password="strong-pass-2")
        self.client = APIClient()
        self.foreign = SoilAnalysis.objects.create(user=self.b, soil_type="clay", soil_ph=5.5)

    def login(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")

    def test_anonymous_user_cannot_read_or_save(self):
        self.assertEqual(self.client.get("/api/soil/").status_code, 401)
        self.assertEqual(self.client.post("/api/soil/", {"soil_ph": 7.0}).status_code, 401)

    def test_users_only_see_own_records(self):
        self.login(self.a)
        result = self.client.get("/api/soil/")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, [])
        created = self.client.post("/api/soil/", {"soil_ph": 6.5, "moisture": 40, "soil_type": "loamy"})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(SoilAnalysis.objects.get(id=created.data["id"]).user, self.a)
        self.assertEqual(len(self.client.get("/api/soil/").data), 1)
        self.assertIn("assessment", created.data)

    def test_out_of_range_values_rejected(self):
        self.login(self.a)
        for payload in ({"soil_ph": 15}, {"moisture": -1}, {"nitrogen": -12}):
            self.assertEqual(self.client.post("/api/soil/", payload).status_code, 400)

    def test_other_users_analysis_is_not_accessible_for_recommendations(self):
        self.login(self.a)
        self.assertEqual(self.client.get(f"/api/crops/recommendations/?soil_id={self.foreign.id}").status_code, 404)

    def test_access_token_can_be_refreshed(self):
        refresh = str(RefreshToken.for_user(self.a))
        result = self.client.post("/api/accounts/token/refresh/", {"refresh": refresh})
        self.assertEqual(result.status_code, 200)
        self.assertIn("access", result.data)
