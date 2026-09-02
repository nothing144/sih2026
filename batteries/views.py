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

from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from analysis.second_life_service import generate_reuse_recommendation
from analysis.models import BatteryAnalysis

class BatteryReuseRecommendationView(APIView):
    permission_classes = [IsAuthenticated, IsEVOwner]

    def post(self, request, pk):
        battery = get_object_or_404(Battery, pk=pk, owner=request.user)
        analysis_id = request.data.get("analysis_id")
        
        if analysis_id:
            analysis = get_object_or_404(BatteryAnalysis, pk=analysis_id, bms_data__battery=battery)
            bms_data = analysis.bms_data
            bms_metrics = getattr(bms_data, "metrics", None) if bms_data else None
            recommendation = generate_reuse_recommendation(battery, bms_metrics, analysis)
        else:
            # Fallback to latest
            latest_bms_data = battery.bms_uploads.order_by("-uploaded_at").first()
            bms_metrics = getattr(latest_bms_data, "metrics", None) if latest_bms_data else None
            
            latest_analysis = None
            if latest_bms_data:
                latest_analysis = BatteryAnalysis.objects.filter(bms_data=latest_bms_data).order_by("-created_at").first()
                
            recommendation = generate_reuse_recommendation(battery, bms_metrics, latest_analysis)
        
        if "error" in recommendation:
            return Response(recommendation, status=503)
            
        return Response(recommendation, status=200)

from analysis.ai_recommendation_service import generate_health_recommendation

class BatteryAIRecommendationView(APIView):
    permission_classes = [IsAuthenticated] # Tester or Owner can view health recommendations

    def get(self, request, pk):
        # We allow anyone authenticated to view if they have access to the battery.
        # Let's ensure the user is either the owner or a tester.
        # The prompt says "Use the existing trusted backend data".
        battery = get_object_or_404(Battery, pk=pk)
        
        # Check permissions: owner or a tester.
        if battery.owner != request.user and not request.user.is_tester:
            raise PermissionDenied("You do not have permission to access this battery's data.")

        # Get the latest BMS Data and Metrics
        latest_bms_data = battery.bms_uploads.order_by("-uploaded_at").first()
        bms_metrics = getattr(latest_bms_data, "metrics", None) if latest_bms_data else None
        
        # Get the latest analysis
        latest_analysis = None
        if latest_bms_data:
            latest_analysis = BatteryAnalysis.objects.filter(bms_data=latest_bms_data).order_by("-created_at").first()

        if not latest_analysis:
            return Response({"error": "No battery analysis found. Run an analysis first."}, status=400)

        recommendation = generate_health_recommendation(battery, latest_analysis, bms_metrics)
        
        if "error" in recommendation:
            return Response(recommendation, status=503)
            
        return Response(recommendation, status=200)

from analysis.second_life_service import generate_readiness_assessment

class BatterySecondLifeReadinessView(APIView):
    permission_classes = [IsAuthenticated, IsEVOwner]

    def post(self, request, pk):
        battery = get_object_or_404(Battery, pk=pk, owner=request.user)
        analysis_id = request.data.get("analysis_id")
        
        if analysis_id:
            analysis = get_object_or_404(BatteryAnalysis, pk=analysis_id, bms_data__battery=battery)
            bms_data = analysis.bms_data
            bms_metrics = getattr(bms_data, "metrics", None) if bms_data else None
            readiness = generate_readiness_assessment(battery, bms_metrics, analysis)
        else:
            # Fallback to latest
            latest_bms_data = battery.bms_uploads.order_by("-uploaded_at").first()
            bms_metrics = getattr(latest_bms_data, "metrics", None) if latest_bms_data else None
            
            latest_analysis = None
            if latest_bms_data:
                latest_analysis = BatteryAnalysis.objects.filter(bms_data=latest_bms_data).order_by("-created_at").first()
                
            readiness = generate_readiness_assessment(battery, bms_metrics, latest_analysis)
        
        if "error" in readiness:
            # We return 400 if it's missing SoH etc, 503 if it's a Gemini error.
            if "required to determine" in readiness["error"]:
                return Response(readiness, status=400)
            return Response(readiness, status=503)
            
        return Response(readiness, status=200)