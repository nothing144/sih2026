from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    OwnerLoginSerializer,
    TesterLoginSerializer,
)

from .permissions import (
    IsEVOwner,
    IsCertifiedTester,
)


# ============================================================
# OWNER REGISTRATION
# ============================================================

class RegisterView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ============================================================
# OWNER LOGIN
# ============================================================

class OwnerLoginView(TokenObtainPairView):

    serializer_class = OwnerLoginSerializer
    permission_classes = [AllowAny]


# ============================================================
# TESTER LOGIN
# ============================================================

class TesterLoginView(TokenObtainPairView):

    serializer_class = TesterLoginSerializer
    permission_classes = [AllowAny]


# ============================================================
# GENERAL PROFILE
# ============================================================

class ProfileView(generics.RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return self.request.user


# ============================================================
# OWNER PROFILE
# ============================================================

class OwnerProfileView(generics.RetrieveUpdateAPIView):
    """
    GET:   returns the owner's profile.
    PATCH: updates editable fields (first_name, last_name, email, phone).
           username and role remain read-only (UserSerializer).
    """

    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
        IsEVOwner,
    ]

    def get_object(self):

        return self.request.user


# ============================================================
# TESTER PROFILE
# ============================================================

class TesterProfileView(generics.RetrieveAPIView):

    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
        IsCertifiedTester,
    ]

    def get_object(self):

        return self.request.user