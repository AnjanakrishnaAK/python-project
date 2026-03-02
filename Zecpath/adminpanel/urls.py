from django.urls import path
from .views import AdminDashboardAPI,EmployerListAPI,ApproveEmployerAPI,UserListAPI, BlockUserAPI,UnblockUserAPI
from .views import AdminJobListAPI,DeleteJobAPI,DisableJobAPI,FlaggedJobsAPI,RemoveSpamJobAPI,ApproveJobAPI,FlagUserAPI
from .views import *
urlpatterns = [

    path("dashboard/",AdminDashboardAPI.as_view(),name="admin-dashboard"),
    path("employers/",EmployerListAPI.as_view(),),
    path("employers/<int:user_id>/approve/",ApproveEmployerAPI.as_view(),),
    path("users/", UserListAPI.as_view()),
    path("users/<int:user_id>/block/", BlockUserAPI.as_view()),
    path("users/<int:user_id>/unblock/",UnblockUserAPI.as_view()),
    path("jobs/", AdminJobListAPI.as_view()),
    path("jobs/<int:job_id>/delete/",DeleteJobAPI.as_view()),
    path("jobs/<int:job_id>/disable/",DisableJobAPI.as_view()),
    path("moderation/jobs/",FlaggedJobsAPI.as_view()),
    path("moderation/jobs/<int:job_id>/remove/",RemoveSpamJobAPI.as_view()),
    path("moderation/jobs/<int:job_id>/approve/",ApproveJobAPI.as_view()),
    path("moderation/users/<int:user_id>/flag/",FlagUserAPI.as_view()),
    path("stats/", PlatformStatsAPIView.as_view()),
    path("user-growth/", UserGrowthAPIView.as_view()),
    path("job-activity/", JobActivityAPIView.as_view()),
    path("audit-logs/", AuditLogListAPIView.as_view()),
]