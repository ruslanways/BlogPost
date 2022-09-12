from rest_framework import permissions

class OwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ('PUT', 'PATCH'):
            return obj.author == request.user
        return obj.author == request.user or request.user.is_staff

