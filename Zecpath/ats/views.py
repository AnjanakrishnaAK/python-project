from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from jobs.models import Job
from accounts.models import CandidateProfile
from ats.services.scoring_service import ATSScoringService
from ats.serializers import ATSScoreSerializer


class CalculateATSScoreAPI(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):

        job = Job.objects.get(id=job_id)
        candidates = CandidateProfile.objects.all()

        results = []

        for candidate in candidates:

            score_obj = ATSScoringService.calculate(candidate, job)

            results.append({
                "candidate_id": candidate.id,
                "score": score_obj.total_score
            })

        return Response({
            "success": True,
            "data": results
        })


class RankedCandidatesAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):

        job = Job.objects.get(id=job_id)

        ranked = ATSScoringService.rank_candidates(job)

        serializer = ATSScoreSerializer(ranked, many=True)

        return Response({
            "success": True,
            "data": serializer.data
        })