from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ("EV_OWNER", "EV Owner"),
        ("CERTIFIED_TESTER", "Certified Tester"),
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="EV_OWNER"
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    def __str__(self):
        return f"{self.username} - {self.role}"