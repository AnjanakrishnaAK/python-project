from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Job, User
from .serializers import JobSerializer, UserSerializer

class HomeAPI(APIView):
    def get(self, request):
        return Response({"message": "Job Portal API is running"})

class JobListAPI(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobCreateAPI(APIView):
    def get(self, request):
        return Response(
            {"message": "Use POST method to create a job"},
            status=status.HTTP_200_OK
        )
    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTestAPI(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


