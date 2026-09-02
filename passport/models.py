from django.db import models
from batteries.models import Battery
from analysis.models import BatteryAnalysis


class BatteryPassport(models.Model):

    class CertificationStatus(models.TextChoices):
        NOT_CERTIFIED = "NOT_CERTIFIED", "Not Certified"
        PENDING_REVIEW = "PENDING_REVIEW", "Pending Review"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    battery = models.ForeignKey(
        Battery,
        on_delete=models.CASCADE,
        related_name="passports"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["battery", "analysis"],
                name="unique_battery_analysis_passport"
            )
        ]

    analysis = models.ForeignKey(
        BatteryAnalysis,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="passports"
    )

    passport_id = models.CharField(
        max_length=100,
        unique=True
    )

    current_soh = models.FloatField(
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

    second_life_status = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    certification_status = models.CharField(
        max_length=50,
        choices=CertificationStatus.choices,
        default=CertificationStatus.NOT_CERTIFIED
    )

    verified_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_passports"
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    verification_notes = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.passport_id