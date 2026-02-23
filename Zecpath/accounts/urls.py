from django.urls import path
from .views import RegisterView

from .views import SignupView, LoginView,CandidateProfileAPI, EmployerProfileAPI
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ResumeUploadAPIView,CandidateListView

from .views import CandidateResumeListView,RecruiterCandidateSearchView
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("candidate/profile/", CandidateProfileAPI.as_view()),
    path("employer/profile/", EmployerProfileAPI.as_view()),

    path('candidate/resume/', ResumeUploadAPIView.as_view()),
    path("candidate/resume/",CandidateResumeListView.as_view(),name="candidate-resume"),
    path("recruiter/candidates/",CandidateListView.as_view(),name="recruiter-candidate-list"),
    path("recruiter/candidates/search/",RecruiterCandidateSearchView.as_view(),name="recruiter-candidate-search"),
]