from rest_framework import permissions

# Role Based Permission
class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        condition_bool = request.user.employee_obj.role.name in ['manager', 'hradmin']
        return condition_bool
