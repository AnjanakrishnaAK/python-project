from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from jobs.models import Job
from applications.models import Application
from .permissions import IsAdminUserRole
from .models import AuditLog
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .serializers import AuditLogSerializer
User = get_user_model()


class AdminDashboardAPI(APIView):

    permission_classes = [IsAdminUserRole]

    def get(self, request):

        data = {

            "total_users":
                User.objects.count(),

            "total_candidates":
                User.objects.filter(
                    role="candidate"
                ).count(),

            "total_employers":
                User.objects.filter(
                    role="employer"
                ).count(),

            "total_jobs":
                Job.objects.count(),

            "total_applications":
                Application.objects.count(),

            "blocked_users":
                User.objects.filter(
                    is_blocked=True
                ).count(),
        }

        return Response({
            "success": True,
            "data": data
        })
    
class EmployerListAPI(APIView):
    
    permission_classes = [IsAdminUserRole]

    def get(self, request):

        employers = User.objects.filter(role="employer")

        data = []

        for emp in employers:

            data.append({
                "id": emp.id,
                "username": emp.username,
                "email": emp.email,
                "approved": emp.is_employer_approved,
                "blocked": emp.is_blocked,
            })

        return Response({
            "success": True,
            "data": data
        })


class ApproveEmployerAPI(APIView):
    permission_classes = [IsAdminUserRole]

    def post(self, request, user_id):

        try:

            employer = User.objects.get(
                id=user_id,
                role="employer"
            )

            employer.is_employer_approved = True
            employer.save()

            AuditLog.objects.create(
                admin=request.user,
                action="APPROVE_EMPLOYER",
                target_user=employer,
                description=f"Approved employer {employer.username}"
            )

            return Response({
                "success": True,
                "message": "Employer approved"
            })

        except User.DoesNotExist:

            return Response({
                "success": False,
                "message": "Employer not found"
            }, status=404)


class UserListAPI(APIView):
    """
    Admin: View all users
    """

    permission_classes = [IsAdminUserRole]

    def get(self, request):

        users = User.objects.all()

        data = []

        for user in users:

            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "blocked": user.is_blocked,
                "approved": getattr(user, "is_employer_approved", False),
            })

        return Response({
            "success": True,
            "data": data
        })


class BlockUserAPI(APIView):
    """
    Admin: Block user
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request, user_id):

        try:

            user = User.objects.get(id=user_id)

            user.is_blocked = True
            user.save()

            AuditLog.objects.create(
                admin=request.user,
                action="BLOCK_USER",
                target_user=user,
                description=f"Blocked user {user.username}"
            )

            return Response({
                "success": True,
                "message": "User blocked"
            })

        except User.DoesNotExist:

            return Response({
                "success": False,
                "message": "User not found"
            }, status=404)


class UnblockUserAPI(APIView):
    """
    Admin: Unblock user
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request, user_id):

        try:

            user = User.objects.get(id=user_id)

            user.is_blocked = False
            user.save()

            AuditLog.objects.create(
                admin=request.user,
                action="UNBLOCK_USER",
                target_user=user,
                description=f"Unblocked user {user.username}"
            )

            return Response({
                "success": True,
                "message": "User unblocked"
            })

        except User.DoesNotExist:

            return Response({
                "success": False,
                "message": "User not found"
            }, status=404)
        
class AdminJobListAPI(APIView):
    """
    Admin: View all jobs
    """

    permission_classes = [IsAdminUserRole]

    def get(self, request):

        jobs = Job.objects.all().order_by("-created_at")

        data = []

        for job in jobs:

            data.append({
                "id": job.id,
                "title": job.title,
                "employer": job.employer.username,
                "active": job.is_active,
                "spam": job.is_spam,
                "created_at": job.created_at
            })

        return Response({
            "success": True,
            "data": data
        })


class DeleteJobAPI(APIView):
    """
    Admin: Delete job permanently
    """

    permission_classes = [IsAdminUserRole]

    def delete(self, request, job_id):

        try:

            job = Job.objects.get(id=job_id)

            AuditLog.objects.create(
                admin=request.user,
                action="DELETE_JOB",
                target_job_id=job.id,
                description=f"Deleted job {job.title}"
            )

            job.delete()

            return Response({
                "success": True,
                "message": "Job deleted"
            })

        except Job.DoesNotExist:

            return Response({
                "success": False,
                "message": "Job not found"
            }, status=status.HTTP_404_NOT_FOUND)


class DisableJobAPI(APIView):
    """
    Admin: Disable job (soft delete)
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request, job_id):

        try:

            job = Job.objects.get(id=job_id)

            job.is_active = False
            job.save()

            AuditLog.objects.create(
                admin=request.user,
                action="DISABLE_JOB",
                target_job_id=job.id,
                description=f"Disabled job {job.title}"
            )

            return Response({
                "success": True,
                "message": "Job disabled"
            })

        except Job.DoesNotExist:

            return Response({
                "success": False,
                "message": "Job not found"
            }, status=404)
        

class FlaggedJobsAPI(APIView):
    """
    Admin: View flagged jobs
    """

    permission_classes = [IsAdminUserRole]

    def get(self, request):

        jobs = Job.objects.filter(is_flagged=True)

        data = []

        for job in jobs:

            data.append({
                "id": job.id,
                "title": job.title,
                "employer": job.employer.username,
                "reason": job.flagged_reason,
            })

        return Response({
            "success": True,
            "data": data
        })


class RemoveSpamJobAPI(APIView):
    """
    Admin: Mark job as spam and disable it
    """

    permission_classes = [IsAdminUserRole]

    def delete(self, request, job_id):

        try:

            job = Job.objects.get(id=job_id)

            job.is_spam = True
            job.is_active = False
            job.save()

            AuditLog.objects.create(
                admin=request.user,
                action="REMOVE_SPAM_JOB",
                target_job_id=job.id,
                description=f"Removed spam job {job.title}"
            )

            return Response({
                "success": True,
                "message": "Spam job removed"
            })

        except Job.DoesNotExist:

            return Response({
                "success": False,
                "message": "Job not found"
            }, status=status.HTTP_404_NOT_FOUND)


class FlagUserAPI(APIView):
    """
    Admin: Flag user account
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request, user_id):

        reason = request.data.get("reason")

        try:

            user = User.objects.get(id=user_id)

            user.is_flagged = True
            user.flag_reason = reason
            user.save()

            AuditLog.objects.create(
                admin=request.user,
                action="FLAG_USER",
                target_user=user,
                description=f"Flagged user {user.username}"
            )

            return Response({
                "success": True,
                "message": "User flagged"
            })

        except User.DoesNotExist:

            return Response({
                "success": False,
                "message": "User not found"
            }, status=404)


class ApproveJobAPI(APIView):
    """
    Admin: Approve flagged job
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request, job_id):

        try:

            job = Job.objects.get(id=job_id)

            job.is_flagged = False
            job.is_spam = False
            job.is_active = True
            job.save()

            AuditLog.objects.create(
                admin=request.user,
                action="APPROVE_JOB",
                target_job_id=job.id,
                description=f"Approved job {job.title}"
            )

            return Response({
                "success": True,
                "message": "Job approved"
            })

        except Job.DoesNotExist:

            return Response({
                "success": False,
                "message": "Job not found"
            }, status=404)
        
class PlatformStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {"message": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        total_users = User.objects.count()
        total_jobs = Job.objects.count()
        total_applications = Application.objects.count()

        active_users = User.objects.filter(is_active=True).count()

        return Response({
            "total_users": total_users,
            "active_users": active_users,
            "total_jobs": total_jobs,
            "total_applications": total_applications
        })


class UserGrowthAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {"message": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        last_7_days = timezone.now() - timedelta(days=7)

        new_users = User.objects.filter(
            date_joined__gte=last_7_days
        ).count()

        return Response({
            "new_users_last_7_days": new_users
        })


class JobActivityAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {"message": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        last_7_days = timezone.now() - timedelta(days=7)

        new_jobs = Job.objects.filter(
            created_at__gte=last_7_days
        ).count()

        applications = Application.objects.filter(
            created_at__gte=last_7_days
        ).count()

        return Response({
            "new_jobs_last_7_days": new_jobs,
            "applications_last_7_days": applications
        })
    
class AuditLogListAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {"message": "Admin only"},
                status=status.HTTP_403_FORBIDDEN
            )

        logs = AuditLog.objects.all()[:100]

        serializer = AuditLogSerializer(logs, many=True)

        return Response(serializer.data)