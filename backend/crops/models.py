from django.db import models


class Crop(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True
    )

    scientific_name = models.CharField(
        max_length=150,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    ideal_soil_types = models.CharField(
        max_length=255,
        blank=True
    )

    min_ph = models.FloatField(
        null=True,
        blank=True
    )

    max_ph = models.FloatField(
        null=True,
        blank=True
    )

    water_requirement = models.CharField(
        max_length=100,
        blank=True
    )

    temperature_min = models.FloatField(
        null=True,
        blank=True
    )

    temperature_max = models.FloatField(
        null=True,
        blank=True
    )

    growing_duration_days = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name
