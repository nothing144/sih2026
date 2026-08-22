from rest_framework import serializers
from .models import BatteryPassport


class BatteryPassportSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatteryPassport

        fields = [
            "id",
            "battery",
            "analysis",
            "passport_id",
            "current_soh",
            "safety_risk",
            "degradation_factors",
            "recommendation",
            "second_life_status",
            "certification_status",
            "verified_by",
            "verified_at",
            "verification_notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
    "id",
    "passport_id",
    "certification_status",
    "verified_by",
    "verified_at",
    "created_at",
    "updated_at",
]