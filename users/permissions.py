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


class IsEVOwnerOrCertifiedTester(BasePermission):
    """
    Allows access to EV Owners and Certified Testers.
    Used for passport detail: owners are limited to their own passports
    (enforced by the view's queryset); certified testers can access
    passports according to the existing tester permissions.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("EV_OWNER", "CERTIFIED_TESTER")
        )

