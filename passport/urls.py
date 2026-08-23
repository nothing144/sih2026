from django.urls import path

from .views import (
    BatteryPassportCreateView,
    BatteryPassportListView,
    BatteryPassportDetailView,
    PassportVerificationListView,
    PassportDecisionsListView,
    PassportVerifyView,
    PassportRejectView,
    PublicPassportVerifyView,
)

urlpatterns = [

    # =========================
    # EV OWNER
    # =========================

    path(
        "create/",
        BatteryPassportCreateView.as_view(),
        name="passport-create"
    ),

    path(
        "list/",
        BatteryPassportListView.as_view(),
        name="passport-list"
    ),

    path(
        "view/<int:pk>/",
        BatteryPassportDetailView.as_view(),
        name="passport-detail"
    ),

    # =========================
    # CERTIFIED TESTER
    # =========================

    path(
        "verification/pending/",
        PassportVerificationListView.as_view(),
        name="passport-pending"
    ),

    path(
        "decisions/",
        PassportDecisionsListView.as_view(),
        name="passport-decisions"
    ),

    path(
        "verify/<int:pk>/",
        PassportVerifyView.as_view(),
        name="passport-verify"
    ),

    path(
        "reject/<int:pk>/",
        PassportRejectView.as_view(),
        name="passport-reject"
    ),

    # =========================
    # PUBLIC (no auth)
    # =========================

    path(
        "public/verify/<str:passport_id>/",
        PublicPassportVerifyView.as_view(),
        name="passport-public-verify"
    ),
]