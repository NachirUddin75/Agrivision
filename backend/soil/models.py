from django.db import models
from django.conf import settings


class SoilAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="soil_analyses")

    SOIL_TYPES = [
        ("loamy", "Loamy"),
        ("sandy", "Sandy"),
        ("clay", "Clay"),
        ("silty", "Silty"),
        ("black", "Black Soil"),
        ("red", "Red Soil"),
        ("other", "Other"),
    ]

    soil_ph = models.FloatField(
        null=True,
        blank=True
    )

    moisture = models.FloatField(
        null=True,
        blank=True
    )

    nitrogen = models.FloatField(
        null=True,
        blank=True
    )

    phosphorus = models.FloatField(
        null=True,
        blank=True
    )

    potassium = models.FloatField(
        null=True,
        blank=True
    )

    soil_type = models.CharField(
        max_length=20,
        choices=SOIL_TYPES,
        default="other"
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    soil_image = models.ImageField(
        upload_to="soil_images/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Soil Analysis - {self.id}"