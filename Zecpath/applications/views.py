from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from applications.models import Application, PipelineStage
from applications.permissions import IsEmployer
from applications.models import Application
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