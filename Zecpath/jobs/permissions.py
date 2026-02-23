from rest_framework.permissions import BasePermission
from accounts.models import CandidateProfile,EmployerProfile


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and CandidateProfile.objects.filter(user=request.user).exists()
        )
    
class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and EmployerProfile.objects.filter(user=request.user).exists()
            and request.user.role == "employer"
        )
    

class IsJobOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.employer.user == request.user
     

class IsApplicationOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.job.employer == request.user

