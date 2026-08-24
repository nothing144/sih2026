from rest_framework import serializers
from .models import Battery, BMSData, BMSMetrics


class BatterySerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Battery

        fields = [
            "id",
            "owner",
            "battery_id",
            "vehicle_model",
            "battery_model",
            "battery_capacity_kwh",
            "chemistry",
            "nominal_voltage",
            "manufacture_date",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]

  # this will change after the model will created when my friend will give me the model filed
class BMSMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BMSMetrics
        fields = [
            "row_count",
            "cycle_count",
            "avg_temperature",
            "min_temperature",
            "max_temperature",
            "avg_voltage",
            "min_voltage",
            "max_voltage",
            "avg_current",
            "total_discharge_duration",
        ]


class BMSDataSerializer(serializers.ModelSerializer):
    metrics = BMSMetricsSerializer(read_only=True)

    class Meta:
        model = BMSData
        fields = [
            "id",
            "battery",
            "file",
            "uploaded_at",
            "metrics",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
        ]