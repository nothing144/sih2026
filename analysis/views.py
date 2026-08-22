from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from batteries.models import BMSData
from .models import BatteryAnalysis
from .serializers import BatteryAnalysisSerializer
from .services import run_battery_analysis


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