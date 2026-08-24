from django.urls import path

from .views import (
    BatteryAnalysisCreateView,
    BatteryAnalysisListView,
    BatteryAnalysisDetailView,
    BmsStatusView,
)

urlpatterns = [

    # =========================
    # BATTERY ANALYSIS
    # =========================

    # Run ML analysis for an uploaded BMS file
    path(
        "create/",
        BatteryAnalysisCreateView.as_view(),
        name="analysis-create"
    ),

    # Get all analyses belonging to the logged-in EV owner
    path(
        "list/",
        BatteryAnalysisListView.as_view(),
        name="analysis-list"
    ),

    # View a single battery analysis
    path(
        "view/<int:pk>/",
        BatteryAnalysisDetailView.as_view(),
        name="analysis-detail"
    ),

    # =========================
    # BMS STATUS (real stored data)
    # =========================

    path(
        "bms/status/",
        BmsStatusView.as_view(),
        name="bms-status"
    ),
]