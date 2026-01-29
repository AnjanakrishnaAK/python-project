from django.urls import path
from .views import JobListCreateView, ApplicationCreateView


urlpatterns = [
path('jobs/', JobListCreateView.as_view()),
path('apply/', ApplicationCreateView.as_view()),
]