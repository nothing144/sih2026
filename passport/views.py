from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .models import BatteryPassport
from .serializers import BatteryPassportSerializer

from users.permissions import IsEVOwner, IsCertifiedTester
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
    # EV Owners see only their own passports; Certified Testers
    # (verification workflow) can read all passports.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "EV_OWNER":
            return BatteryPassport.objects.filter(
                battery__owner=user
            )
        return BatteryPassport.objects.all()


class BatteryPassportDetailView(generics.RetrieveAPIView):
    serializer_class = BatteryPassportSerializer
    # Same read rules as the list view: owners are scoped to their
    # own passports, testers need access for the verification flow.
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "EV_OWNER":
            return BatteryPassport.objects.filter(
                battery__owner=user
            )
        return BatteryPassport.objects.all()


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
# CERTIFIED TESTER - DECIDED PASSPORTS
# =========================

class PassportDecisionsView(generics.ListAPIView):
    """
    GET /api/passport/decisions/

    Certified Tester only. Returns passports that already have a decision
    (VERIFIED or REJECTED), newest decision first. Used by the tester
    Verified / Rejected / History / Certifications pages.
    """

    serializer_class = BatteryPassportSerializer
    permission_classes = [IsCertifiedTester]

    def get_queryset(self):
        return BatteryPassport.objects.filter(
            certification_status__in=[
                BatteryPassport.CertificationStatus.VERIFIED,
                BatteryPassport.CertificationStatus.REJECTED,
            ]
        ).order_by("-verified_at")


# =========================
# PUBLIC PASSPORT VERIFICATION
# =========================

class PublicPassportVerifyView(APIView):
    """
    GET /api/passport/public/verify/<passport_id>/

    Public (no authentication) QR/passport status lookup. Accepts the
    passport_id string (e.g. BP-BAT-1001-AB12CD34) or the numeric pk.
    Exposes ONLY safe, publicly verifiable information - no owner
    personal data (email/phone) is returned.
    """

    permission_classes = [AllowAny]

    def get(self, request, passport_id):
        queryset = BatteryPassport.objects.all()

        if str(passport_id).isdigit():
            queryset = queryset.filter(id=int(passport_id))
        else:
            queryset = queryset.filter(passport_id=passport_id)

        passport = queryset.select_related(
            "battery", "battery__owner", "verified_by"
        ).first()

        if not passport:
            return Response(
                {"detail": "Passport not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            "passport_id": passport.passport_id,
            "battery_id": battery_id_of(passport),
            "vehicle_model": passport.battery.vehicle_model if passport.battery else None,
            "current_soh": passport.current_soh,
            "safety_risk": passport.safety_risk,
            "second_life_status": passport.second_life_status,
            "certification_status": passport.certification_status,
            "verified_at": passport.verified_at,
            "verified_by": (
                passport.verified_by.username if passport.verified_by else None
            ),
        })


def battery_id_of(passport):
    return passport.battery.battery_id if passport.battery else None
