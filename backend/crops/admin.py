from django.contrib import admin

from .models import Crop

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):

    # -----------------------------------------
    # LIST PAGE
    # -----------------------------------------

    list_display = [
        "name",
        "scientific_name",
        "ideal_soil_types",
        "min_ph",
        "max_ph",
        "water_requirement",
        "growing_duration_days",
        "created_at",
    ]

    # -----------------------------------------
    # SEARCH
    # -----------------------------------------

    search_fields = [
        "name",
        "scientific_name",
        "ideal_soil_types",
        "description",
    ]

    # -----------------------------------------
    # FILTERS
    # -----------------------------------------

    list_filter = [
        "water_requirement",
        "created_at",
        "updated_at",
    ]

    # -----------------------------------------
    # SORTING
    # -----------------------------------------

    ordering = [
        "name",
    ]

    # -----------------------------------------
    # EDIT PAGE
    # -----------------------------------------

    fieldsets = (
        (
            "Basic Crop Information",
            {
                "fields": (
                    "name",
                    "scientific_name",
                    "description",
                )
            },
        ),

        (
            "Soil Requirements",
            {
                "fields": (
                    "ideal_soil_types",
                    "min_ph",
                    "max_ph",
                )
            },
        ),

        (
            "Water & Temperature",
            {
                "fields": (
                    "water_requirement",
                    "temperature_min",
                    "temperature_max",
                )
            },
        ),

        (
            "Growing Information",
            {
                "fields": (
                    "growing_duration_days",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    # created/updated are automatically generated
    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    # Number of items per page
    list_per_page = 20
