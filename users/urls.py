from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterView,
    OwnerLoginView,
    TesterLoginView,
    ProfileView,
    OwnerProfileView,
    TesterProfileView,
)


urlpatterns = [

    # Registration
    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    # Login
    path(
        "owner/login/",
        OwnerLoginView.as_view(),
        name="owner-login"
    ),

    path(
        "tester/login/",
        TesterLoginView.as_view(),
        name="tester-login"
    ),

    # JWT token refresh/verify (frontend apiClient calls token/refresh/)
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh"
    ),

    path(
        "token/verify/",
        TokenVerifyView.as_view(),
        name="token-verify"
    ),

    # Profile
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),

    path(
        "owner/profile/",
        OwnerProfileView.as_view(),
        name="owner-profile"
    ),

    path(
        "tester/profile/",
        TesterProfileView.as_view(),
        name="tester-profile"
    ),
]