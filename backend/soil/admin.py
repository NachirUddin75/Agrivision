from django.contrib import admin
from django.utils.html import format_html

from .models import SoilAnalysis


@admin.register(SoilAnalysis)
class SoilAnalysisAdmin(admin.ModelAdmin):

    # -----------------------------------------
    # LIST PAGE
    # -----------------------------------------

    list_display = (
        "id",
        "user",
        "soil_type",
        "soil_ph",
        "moisture",
        "nitrogen",
        "phosphorus",
        "potassium",
        "location",
        "image_preview",
        "created_at",
    )

    # -----------------------------------------
    # SEARCH
    # -----------------------------------------

    search_fields = (
        "user__username",
        "location",
        "soil_type",
    )

    # -----------------------------------------
    # FILTERS
    # -----------------------------------------

    list_filter = (
        "soil_type",
        "created_at",
    )

    # -----------------------------------------
    # SORTING
    # -----------------------------------------

    ordering = (
        "-created_at",
    )

    # -----------------------------------------
    # EDIT PAGE
    # -----------------------------------------

    fieldsets = (
        ("Ownership", {"fields": ("user",)}),
        (
            "Soil Information",
            {
                "fields": (
                    "soil_type",
                    "soil_ph",
                    "moisture",
                )
            },
        ),

        (
            "Nutrient Levels",
            {
                "fields": (
                    "nitrogen",
                    "phosphorus",
                    "potassium",
                )
            },
        ),

        (
            "Location",
            {
                "fields": (
                    "location",
                )
            },
        ),

        (
            "Soil Image",
            {
                "fields": (
                    "soil_image",
                    "image_preview",
                )
            },
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                )
            },
        ),
    )

    # -----------------------------------------
    # READ-ONLY FIELDS
    # -----------------------------------------

    readonly_fields = (
        "created_at",
        "image_preview",
    )

    # -----------------------------------------
    # IMAGE PREVIEW
    # -----------------------------------------

    @admin.display(description="Soil Image")
    def image_preview(self, obj):

        if obj.soil_image:
            return format_html(
                '<img src="{}" width="120" height="90" '
                'style="object-fit: cover; border-radius: 8px;" />',
                obj.soil_image.url,
            )

        return "No image uploaded"

    # -----------------------------------------
    # PAGINATION
    # -----------------------------------------

    list_per_page = 20