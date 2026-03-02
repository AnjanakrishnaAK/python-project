from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from applications.models import Application, PipelineStage
from applications.permissions import IsEmployer
from applications.models import Application
from accounts.permissions import IsCandidate
from .models import Application, ApplicationStatusHistory
from .serializers import ApplicationSerializer
from jobs.models import Job, SavedJob
from notifications.models import Notification

from accounts.models import CandidateProfile

from ats.services.match_service import MatchService


# Create your views here.
class MoveStageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        stage = get_object_or_404(PipelineStage, pk=request.data.get("stage_id"))

        try:
            application.move_stage(stage, request.user)
            return Response({"message": "Stage updated"})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        

class EmployerMoveStageView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):

        application = get_object_or_404(Application, pk=pk)

        stage_id = request.data.get("stage_id")
        new_stage = get_object_or_404(PipelineStage, pk=stage_id)

        try:
            application.move_stage(new_stage, request.user)
            return Response({
                "message": "Stage updated successfully",
                "new_stage": new_stage.name
            })

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=400
            )
        
class ShortlistView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        application = get_object_or_404(Application, pk=pk)
        stage = PipelineStage.objects.get(name="Shortlisted")

        application.move_stage(stage, request.user)

        return Response({"message": "Candidate shortlisted"})
    


class EmployerApplicationStatusUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, application_id):
        try:
            application = Application.objects.get(id=application_id)
        except Application.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)

        new_status = request.data.get("status")

        # ✅ Validate transition
        if not application.can_transition(new_status):
            return Response(
                {"error": f"Cannot change status from {application.status} to {new_status}"},
                status=400
            )

        application.status = new_status
        application.save()

        return Response({"message": "Status updated successfully"})
    

class ShortlistCandidateView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        application = get_object_or_404(Application, pk=pk)

        # Ensure employer owns this job
        if application.job.employer != request.user:
            return Response({"error": "Not allowed"}, status=403)

        try:
            application.change_status("shortlisted")
            return Response({"message": "Candidate shortlisted"})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        

class RejectCandidateView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        application = get_object_or_404(Application, pk=pk)

        if application.job.employer != request.user:
            return Response({"error": "Not allowed"}, status=403)

        try:
            application.change_status("rejected")
            return Response({"message": "Candidate rejected"})
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        

class MoveApplicationStageView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def patch(self, request, pk):
        new_status = request.data.get("status")

        application = get_object_or_404(Application, pk=pk)

        if application.job.employer != request.user:
            return Response({"error": "Not allowed"}, status=403)

        try:
            application.change_status(new_status)
            return Response({
                "message": "Status updated successfully",
                "new_status": application.status
            })
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        

class ApplicationHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        application = get_object_or_404(Application, pk=pk)

        history = application.history.all()

        data = [
            {
                "old_status": h.old_status,
                "new_status": h.new_status,
                "changed_by": h.changed_by.email if h.changed_by else None,
                "action": h.action,
                "timestamp": h.timestamp
            }
            for h in history
        ]

        return Response(data)
    

class CandidateDashboard(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):

        user = request.user

        return Response({

            "applied_jobs":
                Application.objects.filter(
                    candidate=user
                ).count(),

            "saved_jobs":
                SavedJob.objects.filter(
                    candidate=user
                ).count(),

            "interviews":
                Application.objects.filter(
                    candidate=user,
                    status="interview"
                ).count(),

            "notifications":
                Notification.objects.filter(
                    user=user,
                    is_read=False
                ).count(),
        })

class CandidateAppliedJobs(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):

        applications = Application.objects.filter(
            candidate=request.user
        ).select_related("job").order_by("-applied_at")

        data = []

        for app in applications:

            data.append({
                "application_id": app.id,
                "job_id": app.job.id,
                "title": app.job.title,
                "company": app.job.company_name,
                "location": app.job.location,
                "status": app.status,
                "applied_at": app.applied_at
            })

        return Response(data)
    
class ApplyJob(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request, job_id):

        job = Job.objects.get(id=job_id)

        app, created = Application.objects.get_or_create(
            candidate=request.user,
            job=job
        )

        if created:

            ApplicationStatusHistory.objects.create(
                application=app,
                status="applied",
                note="Application submitted"
            )

        return Response({
            "message":
            "Applied" if created else "Already applied"
        })
    
class ApplicationTimeline(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request, application_id):

        timeline = ApplicationStatusHistory.objects.filter(
            application_id=application_id,
            application__candidate=request.user
        )

        data = []

        for t in timeline:

            data.append({

                "status": t.status,
                "note": t.note,
                "date": t.created_at
            })

        return Response(data)
    

class CandidateInterviews(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):

        interviews = Application.objects.filter(
            candidate=request.user,
            status="interview"
        ).select_related("job")

        data = []

        for app in interviews:

            data.append({
                "application_id": app.id,
                "job_id": app.job.id,
                "job_title": app.job.title,
                "company": app.job.company_name,
                "location": app.job.location,
                "status": app.status,
                "applied_at": app.applied_at
            })

        return Response(data)
    

class WithdrawApplication(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def post(self, request, application_id):

        app = Application.objects.get(
            id=application_id,
            candidate=request.user
        )

        app.status = "withdrawn"
        app.save()

        ApplicationStatusHistory.objects.create(
            application=app,
            status="withdrawn",
            note="Candidate withdrew application"
        )

        return Response({
            "message": "Application withdrawn"
        })

class MatchPercentageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):

        candidate = CandidateProfile.objects.get(user=request.user)
        job = Job.objects.get(id=job_id)

        result = MatchService.calculate(candidate, job)

        return Response({
            "success": True,
            "data": result
        })
class RankedCandidatesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):

        # Optional: Allow only employer
        if request.user.role != "employer":
            return Response({"error": "Only employers allowed"}, status=403)

        applications = Application.objects.filter(job_id=job_id)

        ranked_results = []

        for app in applications:
            candidate = app.candidate
            job = app.job

            result = MatchService.calculate(candidate, job)

            ranked_results.append({
                "candidate_id": candidate.id,
                "candidate_name": candidate.user.email,
                "match_percentage": result["match_percentage"]
            })

        # 🔥 Sort by match percentage
        ranked_results = sorted(
            ranked_results,
            key=lambda x: x["match_percentage"],
            reverse=True
        )
# Add ranking numbers
        for index, item in enumerate(ranked_results, start=1):
            item["rank"] = index

        return Response({
            "success": True,
            "data": ranked_results
        })