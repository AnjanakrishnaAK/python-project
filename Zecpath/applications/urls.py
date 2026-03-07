from django.urls import path
from .views import ShortlistCandidateView,RejectCandidateView,CandidateDashboard,CandidateAppliedJobs,ApplyJob,ApplicationTimeline
from .views import  *
urlpatterns = [
    
    
    path("employer/applications/<int:pk>/shortlist/", ShortlistCandidateView.as_view()),
    path("employer/applications/<int:pk>/reject/", RejectCandidateView.as_view()),
    path("employer/applications/<int:pk>/move/", RejectCandidateView.as_view()),
    path("candidate/dashboard/",CandidateDashboard.as_view()),
    path("candidate/applied/",CandidateAppliedJobs.as_view()),
    path("apply/<int:job_id>/",ApplyJob.as_view()),
    path("timeline/<int:application_id>/",ApplicationTimeline.as_view()),
    path("candidate/interviews/",CandidateInterviews.as_view()),
    path("withdraw/<int:application_id>/",WithdrawApplication.as_view()),
    path("match/<int:job_id>/", MatchPercentageAPIView.as_view()),
    path("ranked/<int:job_id>/", RankedCandidatesAPIView.as_view()),
    path("employer/applications/bulk-auto-process/", BulkAutoProcessView.as_view()),
]