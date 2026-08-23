from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import BatteryPassport
from .serializers import BatteryPassportSerializer, PublicPassportVerificationSerializer

from users.permissions import IsEVOwner, IsCertifiedTester, IsEVOwnerOrCertifiedTester
import uuid

# =========================
# OWNER VIEWS
# =========================

class BatteryPassportCreateView(generics.CreateAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsEVOwner]

    def perform_create(self, serializer):

        # Get the battery selected by the EV owner
        battery = serializer.validated_data["battery"]

        # Owner can create passport only for their own battery
        if battery.owner != self.request.user:
            raise PermissionDenied(
                "You can only create a passport for your own battery."
            )

        # Get the battery analysis
        analysis = serializer.validated_data.get("analysis")

        # Analysis is required before creating passport
        if not analysis:
            raise PermissionDenied(
                "Battery analysis is required before creating a passport."
            )

        # Make sure analysis belongs to the selected battery
        if analysis.bms_data.battery != battery:
            raise PermissionDenied(
                "The selected analysis does not belong to this battery."
            )

        # Automatically generate unique passport ID
        passport_id = (
            f"BP-{battery.battery_id}-{uuid.uuid4().hex[:8].upper()}"
        )

        # Copy ML analysis results into passport
        serializer.save(
            passport_id=passport_id,
            current_soh=analysis.soh,
            safety_risk=analysis.safety_risk,
            degradation_factors=analysis.degradation_factors,
            recommendation=analysis.recommendation,
            second_life_status=analysis.second_life,
            certification_status=(
                BatteryPassport.CertificationStatus.PENDING_REVIEW
            ),
        )

class BatteryPassportListView(generics.ListAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsEVOwner]

    def get_queryset(self):
        return BatteryPassport.objects.filter(
            battery__owner=self.request.user
        )


class BatteryPassportDetailView(generics.RetrieveAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [
        IsAuthenticated,
        IsEVOwnerOrCertifiedTester,
    ]

    def get_queryset(self):
        user = self.request.user
        if user.role == "CERTIFIED_TESTER":
            # Testers may view any passport they are reviewing
            return BatteryPassport.objects.all()
        # Owners may only view their own passports
        return BatteryPassport.objects.filter(
            battery__owner=user
        )


# =========================
# CERTIFIED TESTER VIEWS
# =========================

class PassportVerificationListView(generics.ListAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsCertifiedTester]

    def get_queryset(self):
        return BatteryPassport.objects.filter(
            certification_status=(
                BatteryPassport.CertificationStatus.PENDING_REVIEW
            )
        )


class PassportDecisionsListView(generics.ListAPIView):
    """
    Tester-only read-only list of passports that already have a decision
    (VERIFIED or REJECTED). Optional ?status=VERIFIED|REJECTED filter.
    """
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsCertifiedTester]

    def get_queryset(self):
        decided_statuses = [
            BatteryPassport.CertificationStatus.VERIFIED,
            BatteryPassport.CertificationStatus.REJECTED,
        ]

        status_param = self.request.query_params.get("status")

        if status_param is not None and status_param not in decided_statuses:
            return BatteryPassport.objects.none()

        queryset = BatteryPassport.objects.filter(
            certification_status__in=decided_statuses
        )

        if status_param is not None:
            queryset = queryset.filter(certification_status=status_param)

        return queryset.order_by("-verified_at")


class PassportVerifyView(generics.UpdateAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsCertifiedTester]

    queryset = BatteryPassport.objects.all()

    def update(self, request, *args, **kwargs):
        passport = self.get_object()

        if (
            passport.certification_status
            != BatteryPassport.CertificationStatus.PENDING_REVIEW
        ):
            return Response(
                {
                    "detail": "Only passports pending review can be verified."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        passport.certification_status = (
            BatteryPassport.CertificationStatus.VERIFIED
        )

        passport.verified_by = request.user
        passport.verified_at = timezone.now()

        passport.verification_notes = request.data.get(
            "verification_notes",
            ""
        )

        passport.save()

        return Response(
            BatteryPassportSerializer(passport).data,
            status=status.HTTP_200_OK
        )


class PassportRejectView(generics.UpdateAPIView):
    serializer_class = BatteryPassportSerializer
    permission_classes = [IsCertifiedTester]

    queryset = BatteryPassport.objects.all()

    def update(self, request, *args, **kwargs):
        passport = self.get_object()

        if (
            passport.certification_status
            != BatteryPassport.CertificationStatus.PENDING_REVIEW
        ):
            return Response(
                {
                    "detail": "Only passports pending review can be rejected."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        passport.certification_status = (
            BatteryPassport.CertificationStatus.REJECTED
        )

        passport.verified_by = request.user
        passport.verified_at = timezone.now()

        passport.verification_notes = request.data.get(
            "verification_notes",
            ""
        )

        passport.save()

        return Response(
            BatteryPassportSerializer(passport).data,
            status=status.HTTP_200_OK
        )


# =========================
# PUBLIC VERIFICATION (no auth)
# =========================

class PublicPassportVerifyView(generics.RetrieveAPIView):
    """
    Public, read-only passport verification lookup by passport_id.
    Returns only safe verification fields; reflects current DB status.
    """
    permission_classes = [AllowAny]
    serializer_class = PublicPassportVerificationSerializer

    def get_object(self):
        return get_object_or_404(
            BatteryPassport,
            passport_id=self.kwargs["passport_id"]
        )
