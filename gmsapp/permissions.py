from rest_framework import permissions

class IsTenantUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, "tenant") and hasattr(obj, "tenant"):
            if request.user.is_superuser:
                return True
            return request.user.tenant == obj.tenant
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.role and request.user.role.name == "director":
                return True
        return False
