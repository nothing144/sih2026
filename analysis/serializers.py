from rest_framework import serializers
from .models import BatteryAnalysis


class BatteryAnalysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatteryAnalysis
        fields = [
            "id",
            "bms_data",
            "soh",
            "safety_risk",
            "degradation_factors",
            "recommendation",
            "second_life",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]