from rest_framework.permissions import BasePermission
from .models import User


class IsAirlineUser(BasePermission):
    """
    Grants access only to authenticated users whose role is AIRLINE_STAFF
    or AIRLINE_ADMIN and who are actually linked to an airline.

    Stack this alongside IsAuthenticated:
        @permission_classes([IsAuthenticated, IsAirlineUser])
    DRF ANDs multiple permission classes together, so both must pass.
    """
    message = "Only airline staff accounts can access this endpoint."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role in (User.Role.AIRLINE_STAFF, User.Role.AIRLINE_ADMIN)
            and user.airline_id is not None
        )