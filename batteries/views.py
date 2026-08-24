from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Battery, BMSData, BMSMetrics
from .serializers import BatterySerializer, BMSDataSerializer, BMSMetricsSerializer
from .services import compute_bms_metrics
from users.permissions import IsEVOwner


# =========================
# CREATE BATTERY
# =========================

class BatteryCreateView(generics.CreateAPIView):

    serializer_class = BatterySerializer

    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )


# =========================
# LIST BATTERIES
# =========================

class BatteryListView(generics.ListAPIView):

    serializer_class = BatterySerializer

    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def get_queryset(self):
        return Battery.objects.filter(
            owner=self.request.user
        ).order_by("-created_at")


# =========================
# VIEW SINGLE BATTERY
# =========================

class BatteryDetailView(generics.RetrieveAPIView):

    serializer_class = BatterySerializer

    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def get_queryset(self):
        return Battery.objects.filter(
            owner=self.request.user
        )


# =========================
# UPDATE BATTERY
# =========================

class BatteryUpdateView(generics.UpdateAPIView):

    serializer_class = BatterySerializer

    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def get_queryset(self):
        return Battery.objects.filter(
            owner=self.request.user
        )


# =========================
# DELETE BATTERY
# =========================

class BatteryDeleteView(generics.DestroyAPIView):

    serializer_class = BatterySerializer

    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def get_queryset(self):
        return Battery.objects.filter(
            owner=self.request.user
        )

    

class BMSDataCreateView(generics.CreateAPIView):
    serializer_class = BMSDataSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        battery = serializer.validated_data["battery"]

        # Owner can upload BMS data only for their own battery
        if battery.owner != self.request.user:
            raise PermissionDenied(
                "You can only upload BMS data for your own battery."
            )

        bms_data = serializer.save()

        # Derive telemetry aggregates from the uploaded CSV so the
        # dashboard can show real charge cycles / temperature / voltage.
        try:
            metrics = compute_bms_metrics(bms_data.file)
            BMSMetrics.objects.create(bms_data=bms_data, **metrics)
        except Exception:
            # Analysis and upload still succeed even if metric extraction
            # fails; the dashboard shows placeholders for missing metrics.
            pass


class BMSDataListView(generics.ListAPIView):
    serializer_class = BMSDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BMSData.objects.filter(
            battery__owner=self.request.user
        )


class BMSDataDetailView(generics.RetrieveAPIView):
    serializer_class = BMSDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BMSData.objects.filter(
            battery__owner=self.request.user
        )