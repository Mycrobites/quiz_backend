from rest_framework.permissions import BasePermission
class IsTeacher(BasePermission):
    """
    Allow access to teachers only.
    
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role=="Teacher")