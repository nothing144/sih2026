from rest_framework import serializers
from .models import BatteryPassport


class BatteryPassportSerializer(serializers.ModelSerializer):

    # Read-only battery context so testers can see which battery the
    # passport belongs to. Purely additive; existing fields untouched.
    battery_id = serializers.CharField(
        source="battery.battery_id",
        read_only=True
    )

    vehicle_model = serializers.CharField(
        source="battery.vehicle_model",
        read_only=True
    )

    battery_model = serializers.CharField(
        source="battery.battery_model",
        read_only=True
    )

    battery_capacity_kwh = serializers.DecimalField(
        source="battery.battery_capacity_kwh",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    manufacture_date = serializers.DateField(
        source="battery.manufacture_date",
        read_only=True
    )

    owner_username = serializers.CharField(
        source="battery.owner.username",
        read_only=True
    )

    verified_by_username = serializers.CharField(
        source="verified_by.username",
        default=None,
        read_only=True
    )

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
            "battery_id",
            "vehicle_model",
            "battery_model",
            "battery_capacity_kwh",
            "manufacture_date",
            "owner_username",
            "verified_by_username",
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
