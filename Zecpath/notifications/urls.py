from django.urls import path
from .views import CandidateNotifications

urlpatterns = [

    path("notifications/",CandidateNotifications.as_view()),
]