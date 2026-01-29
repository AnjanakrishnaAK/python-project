from rest_framework import generics
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer




class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer




class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer