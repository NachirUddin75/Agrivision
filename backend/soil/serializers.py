from rest_framework import serializers
from .models import SoilAnalysis
from .analysis import analyze_soil

class SoilAnalysisSerializer(serializers.ModelSerializer):
    assessment = serializers.SerializerMethodField()

    class Meta:
        model = SoilAnalysis
        fields = ["id", "soil_ph", "moisture", "nitrogen", "phosphorus", "potassium", "soil_type", "location", "soil_image", "created_at", "assessment"]
        read_only_fields = ["id", "created_at", "assessment"]

    def validate(self, attrs):
        for field, lower, upper in (("soil_ph", 0, 14), ("moisture", 0, 100)):
            value = attrs.get(field)
            if value is not None and not lower <= value <= upper:
                raise serializers.ValidationError({field: f"Must be between {lower} and {upper}."})
        for field in ("nitrogen", "phosphorus", "potassium"):
            value = attrs.get(field)
            if value is not None and not 0 <= value <= 100000:
                raise serializers.ValidationError({field: "Must be a non-negative value not exceeding 100000."})
        return attrs

    def get_assessment(self, obj):
        return analyze_soil(obj)
