from django.urls import path
from .views import EmployerMoveStageView,ShortlistCandidateView,RejectCandidateView

urlpatterns = [
    path("employer/applications/<int:pk>/move/",EmployerMoveStageView.as_view()),
    path("employer/applications/<int:pk>/shortlist/", ShortlistCandidateView.as_view()),
    path("employer/applications/<int:pk>/reject/", RejectCandidateView.as_view()),
    path("employer/applications/<int:pk>/move/", RejectCandidateView.as_view()),
    
]