from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from batteries.models import Battery, BMSData
from users.permissions import IsEVOwner

from .models import BatteryAnalysis
from .serializers import BatteryAnalysisSerializer
from .services import run_battery_analysis, extract_latest_telemetry


class BatteryAnalysisCreateView(generics.CreateAPIView):
    serializer_class = BatteryAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        bms_id = request.data.get("bms_data")

        if not bms_id:
            return Response(
                {
                    "detail": "bms_data is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            bms_data = BMSData.objects.get(
                id=bms_id,
                battery__owner=request.user
            )
        except BMSData.DoesNotExist:
            return Response(
                {
                    "detail": "BMS data not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Run ML analysis
            result = run_battery_analysis(
                bms_data.file
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save ML result
        analysis = BatteryAnalysis.objects.create(
            bms_data=bms_data,
            soh=result["soh_prediction"],
            safety_risk=result["risk"],
            degradation_factors=result["degradation_factors"],
            recommendation=result["recommendation"],
            second_life=result["second_life"],
        )

        serializer = self.get_serializer(analysis)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class BatteryAnalysisListView(generics.ListAPIView):
    serializer_class = BatteryAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BatteryAnalysis.objects.filter(
            bms_data__battery__owner=self.request.user
        )


class BatteryAnalysisDetailView(generics.RetrieveAPIView):
    serializer_class = BatteryAnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BatteryAnalysis.objects.filter(
            bms_data__battery__owner=self.request.user
        )


class BmsStatusView(APIView):
    """
    GET /api/analysis/bms/status/

    Per-battery BMS status for the logged-in EV Owner, derived ONLY from
    real stored data:
      - last_bms_upload : uploaded_at of the latest BMSData CSV
      - telemetry       : latest row of that stored CSV (real file content)
      - analysis        : stored ML result (SOH / safety risk) if it was run

    This is NOT real-time telemetry. Readings are as of the upload.
    Owner scoping: every query starts from request.user's batteries, so an
    owner can never see another owner's BMS data.
    """

    permission_classes = [IsAuthenticated, IsEVOwner]

    def get(self, request):
        results = []

        batteries = Battery.objects.filter(
            owner=request.user
        ).order_by("id")

        for battery in batteries:
            entry = {
                "battery": battery.id,
                "battery_id": battery.battery_id,
                "has_bms_data": False,
                "last_bms_upload": None,
                "telemetry": None,
                "analysis": None,
            }

            latest_bms = battery.bms_uploads.order_by(
                "-uploaded_at"
            ).first()

            if latest_bms:
                entry["has_bms_data"] = True
                entry["last_bms_upload"] = latest_bms.uploaded_at

                try:
                    entry["telemetry"] = extract_latest_telemetry(
                        latest_bms.file
                    )
                except Exception:
                    # Unreadable/corrupt file: report no telemetry rather
                    # than failing the whole status endpoint.
                    entry["telemetry"] = None

                latest_analysis = latest_bms.analyses.order_by(
                    "-created_at"
                ).first()

                if latest_analysis:
                    entry["analysis"] = {
                        "soh": latest_analysis.soh,
                        "safety_risk": latest_analysis.safety_risk,
                        "created_at": latest_analysis.created_at,
                    }

            results.append(entry)

        return Response({"results": results})
