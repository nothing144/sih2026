from django.urls import path

from .views import (
    BatteryCreateView,
    BatteryListView,
    BatteryDetailView,
    BatteryUpdateView,
    BatteryDeleteView,
    BMSDataCreateView,
    BMSDataListView,
    BMSDataDetailView,
)

urlpatterns = [

    # -------------------------
    # Battery APIs
    # -------------------------

    path(
        "create/",
        BatteryCreateView.as_view(),
        name="battery-create"
    ),

    path(
        "list/",
        BatteryListView.as_view(),
        name="battery-list"
    ),

    path(
        "view/<int:pk>/",
        BatteryDetailView.as_view(),
        name="battery-detail"
    ),

    path(
        "update/<int:pk>/",
        BatteryUpdateView.as_view(),
        name="battery-update"
    ),

    path(
        "delete/<int:pk>/",
        BatteryDeleteView.as_view(),
        name="battery-delete"
    ),

    # -------------------------
    # BMS / Charging APIs
    # -------------------------

    path(
        "bms/create/",
        BMSDataCreateView.as_view(),
        name="bms-create"
    ),

    path(
        "bms/list/",
        BMSDataListView.as_view(),
        name="bms-list"
    ),

    path(
        "bms/view/<int:pk>/",
        BMSDataDetailView.as_view(),
        name="bms-detail"
    ),
]