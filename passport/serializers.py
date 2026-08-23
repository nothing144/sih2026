from rest_framework import serializers
from .models import BatteryPassport


class BatteryPassportSerializer(serializers.ModelSerializer):

    # Read-only identity fields exposed for tester-facing views
    battery_id = serializers.CharField(source="battery.battery_id", read_only=True)
    owner_username = serializers.CharField(source="battery.owner.username", read_only=True)
    vehicle_model = serializers.CharField(source="battery.vehicle_model", read_only=True)

    class Meta:
        model = BatteryPassport

        fields = [
            "id",
            "battery",
            "analysis",
            "passport_id",
            "battery_id",
            "owner_username",
            "vehicle_model",
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


class PublicPassportVerificationSerializer(serializers.ModelSerializer):
    """
    Safe, public, read-only verification payload.
    Deliberately excludes owner identity, contact info, tester identity,
    analysis internals and verification notes.
    """

    battery_id = serializers.CharField(source="battery.battery_id", read_only=True)
    vehicle_model = serializers.CharField(source="battery.vehicle_model", read_only=True)

    class Meta:
        model = BatteryPassport

        fields = [
            "passport_id",
            "battery_id",
            "vehicle_model",
            "current_soh",
            "safety_risk",
            "certification_status",
            "verified_at",
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