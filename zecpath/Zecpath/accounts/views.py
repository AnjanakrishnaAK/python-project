from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, UserSerializer,CandidateProfileSerializer,EmployerProfileSerializer

from rest_framework import generics, status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,CandidateProfile,EmployerProfile
from .serializers import SignupSerializer, LoginSerializer

from accounts.permissions import IsAdmin,IsSelfOrAdmin

from rest_framework.generics import RetrieveUpdateDestroyAPIView,CreateAPIView

from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone
from rest_framework.parsers import MultiPartParser
from .validators import validate_resume
from .services import upload_or_replace_resume
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "email": user.email,
            "role": user.role
        })
class ProfileView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully",
                    "email": user.email,
                    "role": user.role
                },
                status=status.HTTP_201_CREATED
            )

       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class LoginView(APIView):
    permission_classes = [AllowAny]   

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "role": user.role,
                "email": user.email
            },
            status=status.HTTP_200_OK
        )
    

class UserListAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "User list"})
    



class CandidateProfileCreateAPI(CreateAPIView):
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CandidateProfileAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        qs = CandidateProfile.objects.filter(is_active=True)
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.save()
class EmployerProfileAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = EmployerProfileSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def get_queryset(self):
        qs = EmployerProfile.objects.filter(is_active=True)

        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return qs

        return qs.filter(user=self.request.user)

    def perform_destroy(self, instance):
        
        instance.is_active = False
        instance.deleted_at = timezone.now()
        instance.save()

class EmployerVerifyAPI(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        employer = EmployerProfile.objects.get(pk=pk)

        if not all([
            employer.company_name,
            employer.company_domain,
            employer.company_size,
            employer.industry,
        ]):
            return Response(
                {"error": "Employer profile is incomplete"},
                status=400
            )

        employer.is_verified = True
        employer.save()
        return Response({"status": "Verified"})
    
class ResumeUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        if not hasattr(request.user, 'candidateprofile'):
            return Response(
                {"error": "Candidate profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES.get('resume')
        if not file:
            return Response(
                {"error": "Resume file is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        validate_resume(file)

        profile = request.user.candidateprofile
        resume = upload_or_replace_resume(profile, file)

        return Response({
            "message": "Resume uploaded successfully",
            "resume_id": resume.id,
            "version": resume.version
        }, status=status.HTTP_200_OK)
    
class CandidateResumeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resumes = Resume.objects.filter(
            candidate__user=request.user
        )
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)