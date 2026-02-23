from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from jobs.models import Job, JobApplication
from jobs.serializers import JobApplicationSerializer,EmployerJobApplicationSerializer,JobCreateSerializer,JobUpdateSerializer,PublicJobSerializer,EmployerJobSerializer,ApplyJobSerializer,EmployerApplicationRecordSerializer,CandidateApplicationRecordSerializer
from jobs.permissions import IsEmployer
from accounts.models import CandidateProfile,EmployerProfile,Resume
from accounts.permissions import IsAdmin
from django.db.models import Q,Count
from .pagination import JobCursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobFilter
from rest_framework.generics import RetrieveAPIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from jobs.serializers import JobSerializer

class ApplyJobAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, job_id):
        #  Candidate-only check
        if request.user.role != 'candidate':
            return Response(
                {"error": "Only candidates can apply for jobs."},
                status=status.HTTP_403_FORBIDDEN
            )
        #  Get candidate profile
        candidate = get_object_or_404(
            CandidateProfile,
            user=request.user
        )
        #  Get job
        job = get_object_or_404(
            Job.objects.select_related('employer'),
            id=job_id
        )
        #  Job status check
        if job.status != 'active':
            return Response(
                {"error": "This job is not accepting applications."},
                status=status.HTTP_400_BAD_REQUEST
            )
        #  Duplicate prevention
        if JobApplication.objects.filter(
            job=job,
            candidate=candidate
        ).exists():
            return Response(
                {"error": "You have already applied to this job."},
                status=status.HTTP_400_BAD_REQUEST
            )
        #  Resume binding (validate resume belongs to candidate)
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "Resume ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        resume = get_object_or_404(
            Resume,
            id=resume_id,
            candidate=candidate  #  Ownership check
        )
        #  Create application
        JobApplication.objects.create(
            job=job,
            candidate=candidate,
            resume=resume
        )
        return Response(
            {"message": "Job applied successfully."},
            status=status.HTTP_201_CREATED
        )
    
class EmployerJobApplicationsView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request, job_id):
        employer = EmployerProfile.objects.get(user=request.user)

        job = Job.objects.get(
            id=job_id,
            employer=employer
        )

        applications = JobApplication.objects.filter(
            job=job
        ).select_related("candidate", "resume")

        serializer = EmployerJobApplicationSerializer(
            applications,
            many=True
        )

        return Response(serializer.data)
    
class EmployerJobCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request):
        employer = EmployerProfile.objects.get(user=request.user)

        serializer = JobCreateSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save(
                employer=employer,
                status='draft'  # always start as draft
            )
            return Response(
                {
                    "message": "Job created successfully",
                    "job_id": job.id,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AdminVerifyJobView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, job_id):
        job = Job.objects.get(id=job_id)

        job.is_verified = True
        job.save()

        return Response(
            {"message": "Job verified successfully"},
            status=status.HTTP_200_OK
        )
class EmployerJobUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]
    def put(self, request, pk):
        if request.user.role != 'employer':
            return Response({"error": "Access denied"}, status=403)

        job = get_object_or_404(Job, id=pk, employer=request.user)
        serializer = JobSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    
class PublicJobListView(ListAPIView):
    serializer_class = PublicJobSerializer
    permission_classes = [AllowAny]
    pagination_class = JobCursorPagination
    queryset = Job.objects.filter(status='active')

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_class = JobFilter

    # Keyword search
    search_fields = [
        'title',
        'description',
        'location',
        'skills__name'
    ]

    ordering_fields = [
        'created_at',
        'salary_min',
        'experience_min'
    ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'employer'
        ).prefetch_related(
            'skills'
        ).distinct()
class LatestJobListView(ListAPIView):
    serializer_class = PublicJobSerializer
    permission_classes = [AllowAny]
    pagination_class = JobCursorPagination

    def get_queryset(self):
        return Job.objects.filter(
            status='active'
        ).order_by('-created_at')
    
class EmployerJobListView(ListAPIView):
    serializer_class = EmployerJobSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'employer':
            return Response({"error": "Access denied"}, status=403)

        jobs = Job.objects.filter(employer=request.user)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

class CandidateAppliedJobsView(ListAPIView):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(
            candidate__user=self.request.user
        ).select_related('job')
    

    
class EmployerApplicationRecordsAPIView(ListAPIView):
    serializer_class = EmployerApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "employerprofile"):
            return JobApplication.objects.none()

        return JobApplication.objects.select_related(
            'candidate__user',
            'job'
        ).filter(
            job__employer=user.employerprofile
        ).order_by('-applied_at')
    

class ApplicationDetailAPIView(RetrieveAPIView):
    serializer_class = CandidateApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Candidate can view own
        if hasattr(user, "candidateprofile"):
            return JobApplication.objects.filter(
                candidate=user.candidateprofile
            )

        # Employer can view applications of their jobs
        if hasattr(user, "employerprofile"):
            return JobApplication.objects.filter(
                job__employer=user.employerprofile
            )

        return JobApplication.objects.none()
    

class MyApplicationTrackingAPIView(ListAPIView):
    serializer_class = CandidateApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "candidateprofile"):
            return JobApplication.objects.none()

        queryset = JobApplication.objects.select_related(
            'job',
            'job__employer',
            'resume'
        ).filter(
            candidate=user.candidateprofile
        ).order_by('-applied_at')

        # Optional filters
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        return queryset
    
class MyApplicationDetailAPIView(RetrieveAPIView):
    serializer_class = CandidateApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "candidateprofile"):
            return JobApplication.objects.none()

        return JobApplication.objects.select_related(
            'job',
            'job__employer',
            'resume'
        ).filter(
            candidate=user.candidateprofile
        )
    
class EmployerApplicationTrackingAPIView(ListAPIView):
    serializer_class = EmployerApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "employerprofile"):
            return JobApplication.objects.none()

        queryset = JobApplication.objects.select_related(
            'candidate__user',
            'job',
            'resume',
        ).filter(
            job__employer=user.employerprofile
        ).order_by('-applied_at')

        # Optional filters
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        job_id = self.request.query_params.get('job_id')
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        return queryset
    

class UpdateApplicationStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        application = get_object_or_404(
            JobApplication,
            id=pk,
            job__employer=user
        )

        new_status = request.data.get("status")

        valid_status = ["applied", "shortlisted", "rejected", "hired"]

        if new_status not in valid_status:
            return Response({"error": "Invalid status"}, status=400)

        application.status = new_status
        application.save(update_fields=["status"])

        return Response({"message": "Status updated successfully"})
    
class BulkApplicationStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        ids = request.data.get("application_ids", [])
        status_value = request.data.get("status")

        valid_status = ["applied", "shortlisted", "rejected", "hired"]

        if status_value not in valid_status:
            return Response({"error": "Invalid status"}, status=400)

        applications = JobApplication.objects.filter(
            id__in=ids,
            job__employer=user
        )

        applications.update(status=status_value)

        return Response({"message": "Bulk update successful"})
    

class EmployerPipelineSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        job_id = request.query_params.get("job_id")

        applications = JobApplication.objects.filter(
            job__id=job_id,
            job__employer=user
        )

        summary = applications.aggregate(
            applied=Count("id", filter=Q(status="applied")),
            shortlisted=Count("id", filter=Q(status="shortlisted")),
            rejected=Count("id", filter=Q(status="rejected")),
            hired=Count("id", filter=Q(status="hired")),
        )

        return Response(summary)
    

class EmployerCloseJobView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != "employer":
            return Response({"error": "Only employers allowed"}, status=403)

        job = get_object_or_404(Job, id=pk, employer=request.user)

        job.status = "closed"
        job.save(update_fields=["status"])

        return Response({"message": "Job closed successfully"})
    

class EmployerApplicantListAPIView(ListAPIView):
    serializer_class = EmployerApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role != "employer":
            return JobApplication.objects.none()

        queryset = JobApplication.objects.select_related(
            "candidate__user",
            "job"
        ).filter(
            job__employer=user
        )

        job_id = self.request.query_params.get("job_id")
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(candidate__user__email__icontains=search) |
                Q(candidate__user__first_name__icontains=search) |
                Q(candidate__user__last_name__icontains=search) |
                Q(job__title__icontains=search)
            )

        return queryset.order_by("-applied_at")
    
class EmployerAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        # Jobs count
        total_jobs = Job.objects.filter(
            employer=user
        ).count()

        # Applications queryset
        applications = JobApplication.objects.filter(
            job__employer=user
        )

        total_applications = applications.count()

        shortlisted = applications.filter(
            status="shortlisted"
        ).count()

        rejected = applications.filter(
            status="rejected"
        ).count()

        hired = applications.filter(
            status="hired"
        ).count()
        shortlist_ratio = 0
        if total_applications > 0:
            shortlist_ratio = round(
                (shortlisted / total_applications) * 100,
                2
            )

        return Response({
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "shortlisted": shortlisted,
            "rejected": rejected,
            "hired": hired,
            "shortlist_ratio_percentage": shortlist_ratio
        })
    

class EmployerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        # Jobs
        jobs = Job.objects.filter(employer=user)

        total_jobs = jobs.count()
        active_jobs = jobs.filter(status="active").count()
        closed_jobs = jobs.filter(status="closed").count()
        draft_jobs = jobs.filter(status="draft").count()

        # Applications
        applications = JobApplication.objects.filter(
            job__employer=user
        )

        total_applications = applications.count()
        shortlisted = applications.filter(status="shortlisted").count()
        hired = applications.filter(status="hired").count()

        return Response({
            "jobs": {
                "total": total_jobs,
                "active": active_jobs,
                "closed": closed_jobs,
                "draft": draft_jobs,
            },
            "applications": {
                "total": total_applications,
                "shortlisted": shortlisted,
                "hired": hired,
            }
        })
    

class EmployerApplicationsPerJobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        jobs = Job.objects.filter(employer=user).annotate(
            application_count=Count("job_applications")
        )

        data = [
            {
                "job_id": job.id,
                "job_title": job.title,
                "applications": job.application_count
            }
            for job in jobs
        ]

        return Response(data)
    

class EmployerRecentApplicationsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        applications = JobApplication.objects.select_related(
            "candidate__user",
            "job"
        ).filter(
            job__employer=user
        ).order_by("-applied_at")[:5]

        data = [
            {
                "candidate_email": app.candidate.user.email,
                "job_title": app.job.title,
                "status": app.status,
                "applied_at": app.applied_at,
            }
            for app in applications
        ]

        return Response(data)
    

class EmployerJobPipelineAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role != "employer":
            return Response({"error": "Access denied"}, status=403)

        job_id = request.query_params.get("job_id")
        if not job_id:
            return Response({"error": "job_id required"}, status=400)

        job = get_object_or_404(Job, id=job_id, employer=user)

        applications = JobApplication.objects.select_related(
            "candidate__user"
        ).filter(job=job)

        serializer = EmployerApplicationRecordSerializer(applications, many=True)
        return Response(serializer.data)