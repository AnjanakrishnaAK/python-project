from django.urls import path
from jobs.views import EmployerJobApplicationsView,EmployerJobCreateView,AdminVerifyJobView,EmployerJobUpdateView,PublicJobListView,LatestJobListView,EmployerJobListView,CandidateAppliedJobsView,ApplyJobAPIView
from jobs.views import MyApplicationTrackingAPIView,MyApplicationDetailAPIView,EmployerApplicationTrackingAPIView,UpdateApplicationStatusAPIView,EmployerCloseJobView,EmployerAnalyticsAPIView,EmployerDashboardAPIView
from jobs.views import EmployerJobPipelineAPIView,BulkApplicationStatusUpdateAPIView,EmployerPipelineSummaryAPIView
urlpatterns = [
    path('jobs/<int:job_id>/apply/', ApplyJobAPIView.as_view()),
    path('employer/jobs/<int:job_id>/applications/',EmployerJobApplicationsView.as_view()),
    path('employer/jobs/create/',EmployerJobCreateView.as_view(),name='employer-job-create'),
    path('admin/jobs/<int:job_id>/verify/',AdminVerifyJobView.as_view(),name='admin-job-verify'),
    path('employer/jobs/<int:job_id>/update/',EmployerJobUpdateView.as_view(),name='employer-job-update'),
    path('public/jobs/', PublicJobListView.as_view()),
    path('public/jobs/latest/', LatestJobListView.as_view()),
    path('employer/jobs/', EmployerJobListView.as_view()),
    path('candidate/applied-jobs/', CandidateAppliedJobsView.as_view()),
    path('apply/', ApplyJobAPIView.as_view(), name='apply-job'),
    path('applications/my/', MyApplicationTrackingAPIView.as_view()),
    path('applications/my/<int:pk>/', MyApplicationDetailAPIView.as_view()),
    path('applications/employer/', EmployerApplicationTrackingAPIView.as_view()),
    path("employer/pipeline/<int:pk>/", UpdateApplicationStatusAPIView.as_view()),
    path('employer/jobs/<int:pk>/close/', EmployerCloseJobView.as_view()),
    path("employer/analytics/", EmployerAnalyticsAPIView.as_view()),
    path("employer/dashboard/", EmployerDashboardAPIView.as_view()),
    path("employer/pipeline/", EmployerJobPipelineAPIView.as_view()),
    path("employer/pipeline/bulk-update/", BulkApplicationStatusUpdateAPIView.as_view()),
    path("employer/pipeline-summary/", EmployerPipelineSummaryAPIView.as_view()),
]
