from django.db import models
from batteries.models import BMSData


class BatteryAnalysis(models.Model):
    bms_data = models.ForeignKey(
        BMSData,
        on_delete=models.CASCADE,
        related_name="analyses"
    )

    soh = models.FloatField(
        null=True,
        blank=True
    )

    safety_risk = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    degradation_factors = models.JSONField(
        null=True,
        blank=True
    )

    recommendation = models.TextField(
        null=True,
        blank=True
    )

    second_life = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Analysis {self.id} - BMS {self.bms_data.id}"