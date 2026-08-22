from rest_framework import serializers
from .models import Battery, BMSData


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
class BMSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BMSData
        fields = [
            "id",
            "battery",
            "file",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "uploaded_at",
        ]