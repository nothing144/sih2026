from rest_framework import serializers
from .models import BatteryAnalysis


class BatteryAnalysisSerializer(serializers.ModelSerializer):
    is_second_life_eligible = serializers.SerializerMethodField()

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
            "is_second_life_eligible",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]
        
    def get_is_second_life_eligible(self, obj):
        from django.conf import settings
        threshold = getattr(settings, 'SECOND_LIFE_SOH_THRESHOLD', 80)
        if obj.soh is None:
            return False
        return obj.soh <= threshold