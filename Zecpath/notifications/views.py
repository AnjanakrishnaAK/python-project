from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.permissions import IsCandidate
from .models import Notification
from .serializers import NotificationSerializer


class CandidateNotifications(APIView):

    permission_classes = [IsAuthenticated, IsCandidate]

    def get(self, request):

        notifications = Notification.objects.filter(
            user=request.user
        )

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(serializer.data)