from django.urls import path
from .views import JobListAPI, JobCreateAPI, UserTestAPI,HomeAPI

urlpatterns = [
    path('', HomeAPI.as_view()), 
    path('jobs/', JobListAPI.as_view()),
    path('jobs/create/', JobCreateAPI.as_view()),
    path('users/', UserTestAPI.as_view()),
]