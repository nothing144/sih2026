from django.conf import settings
from django.db import models


class Battery(models.Model):

    # EV Owner who owns this battery
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="batteries"
    )

    # Unique Battery ID
    battery_id = models.CharField(
        max_length=100,
        unique=True
    )

    # Vehicle information
    vehicle_model = models.CharField(
        max_length=100
    )

    # Battery information
    battery_model = models.CharField(
        max_length=100,
        blank=True
    )

    battery_capacity_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    manufacture_date = models.DateField(
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.battery_id} - {self.vehicle_model}"



# this will change after the model will created when my friend will give me the model filed
class BMSData(models.Model):
    battery = models.ForeignKey(
        Battery,
        on_delete=models.CASCADE,
        related_name="bms_uploads"
    )

    file = models.FileField(
    upload_to="bms_uploads/"
)

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.battery.battery_id} - BMS File"