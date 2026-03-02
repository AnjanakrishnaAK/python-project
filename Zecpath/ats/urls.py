from django.urls import path
from ats.views import (
    CalculateATSScoreAPI,
    RankedCandidatesAPI
)

urlpatterns = [

    path("jobs/<int:job_id>/calculate/",CalculateATSScoreAPI.as_view()),
    path("jobs/<int:job_id>/ranking/",RankedCandidatesAPI.as_view()),
]