from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, UserSerializer,CandidateProfileSerializer,EmployerProfileSerializer,CandidateSerializer

from rest_framework import generics, status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,CandidateProfile,EmployerProfile
from .serializers import SignupSerializer, LoginSerializer

from accounts.permissions import IsAdmin,IsSelfOrAdmin,IsEmployer

from rest_framework.generics import RetrieveUpdateDestroyAPIView,CreateAPIView,ListAPIView

from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone
from rest_framework.parsers import MultiPartParser
from .validators import validate_resume
from .services import upload_or_replace_resume,ProfileService
from rest_framework import status

from .models import Resume
from .serializers import ResumeSerializer,ProfileSerializer

from rest_framework.pagination import PageNumberPagination
from .pagination import ZecpathPagination 
from django.db.models import Q

from django.db import models
from .models import User
from .serializers import AdminProfileSerializer

    
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
    permission_classes = [AllowAny]

    def get(self, request):
        resumes = Resume.objects.filter(
            candidate__user=request.user
        )
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)
    
class ZecpathPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50

class CandidateListView(ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]
    pagination_class = ZecpathPagination

    def get_queryset(self):
        user = self.request.user

        if user.role != User.EMPLOYER:
            return CandidateProfile.objects.none()

        return (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related("skills")
            .filter(
                user__role=User.CANDIDATE,
                is_active=True
            )
            .order_by("-created_at")   # 👈 FIX
        )
    
class RecruiterCandidateListView(ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]
    pagination_class = ZecpathPagination

    def get_queryset(self):
        return (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related("skills")
            .filter(
                user__role=User.CANDIDATE,
                is_active=True
            )
        )
class RecruiterCandidateSearchView(ListAPIView):
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]
    pagination_class = ZecpathPagination

    def get_queryset(self):
        queryset = (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related("skills")
            .filter(
                user__role=User.CANDIDATE,
                is_active=True
            )
        )

        # 🔍 Keyword search
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(user__email__icontains=q) |
                Q(education__icontains=q) |
                Q(current_location__icontains=q) |
                Q(skills__name__icontains=q)
            ).distinct()

        #  Location filter
        location = self.request.query_params.get("location")
        if location:
            queryset = queryset.filter(
                current_location__icontains=location
            )

        #  Experience filters
        min_exp = self.request.query_params.get("min_exp")
        if min_exp:
            queryset = queryset.filter(experience_years__gte=min_exp)

        max_exp = self.request.query_params.get("max_exp")
        if max_exp:
            queryset = queryset.filter(experience_years__lte=max_exp)

        return queryset
    

class AdminProfileAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not request.user.is_staff:
            return Response(
                {"success": False, "message": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdminProfileSerializer(request.user)

        return Response({
            "success": True,
            "data": serializer.data
        })
    




