from rest_framework import permissions

# Role Based Permission
class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name__in=['manager','hradmin']).exists()
        # return super().has_permission(request, view)
# class IsManagerorAdmin
