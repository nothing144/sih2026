from rest_framework.permissions import BasePermission


class IsEVOwner(BasePermission):
    """
    Allows access only to EV Owners.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "EV_OWNER"
        )


class IsCertifiedTester(BasePermission):
    """
    Allows access only to Certified Testers.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "CERTIFIED_TESTER"
        )

