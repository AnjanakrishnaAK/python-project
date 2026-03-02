from django.urls import path
from .views import ResumeUploadAPI, ResumeUploadParseAPI,ResumeUploadView


urlpatterns = [
    path("upload/", ResumeUploadAPI.as_view()),
    path("upload/", ResumeUploadParseAPI.as_view()),
    path("upload/", ResumeUploadView.as_view()),
]