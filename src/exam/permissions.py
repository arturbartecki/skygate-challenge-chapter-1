from rest_framework.permissions import BasePermission

SAFE_METHODS = ['GET', 'POST', 'HEAD', 'OPTIONS']


class IsOwnerOrReadOnly(BasePermission):
    """Permits only owner to make any changes or delete"""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or obj.owner == request.user:
            return True
        return False
