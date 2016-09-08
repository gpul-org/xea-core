from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    def get_owner(self, obj):
        return obj

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user == self.get_owner(obj):
            return True
        return False


class IsPlaceOwnerOrStaff(IsAdminOrSelf):
    def get_owner(self, obj):
        return obj.owner

