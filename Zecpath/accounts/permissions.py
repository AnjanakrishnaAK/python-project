from rest_framework.permissions import BasePermission

class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in self.allowed_roles
        )
    
class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.user == request.user
    
class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "employer"
    
class IsCandidate(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated and
            hasattr(request.user, "profile") and
            request.user.profile.role == "candidate"
        )
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
        )
class IsAdmin(HasRole):
    allowed_roles = ['ADMIN']

class IsEmployer(HasRole):
    allowed_roles = ['EMPLOYER']

class IsCandidate(HasRole):
    allowed_roles = ['CANDIDATE']