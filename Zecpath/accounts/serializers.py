import re

from rest_framework import serializers
from .models import User,CandidateProfile,EmployerProfile, Resume,Skill
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'role')

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','role','is_verified')



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            email=data['email'],
            password=data['password']
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role
        }


class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = "__all__"
        read_only_fields = (
            "user",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        )

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Experience years cannot be negative."
            )
        return value

    def validate_expected_salary(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "Expected salary must be greater than zero."
            )
        return value

    def validate(self, attrs):
        
        request = self.context.get("request")
        if request and request.method in ["PUT", "PATCH"]:
            skills = attrs.get("skills")
            if skills is not None and len(skills) == 0:
                raise serializers.ValidationError(
                    {"skills": "At least one skill is required."}
                )
        return attrs
    
class CandidateProfileSerializer(serializers.ModelSerializer):
        resume_url = serializers.SerializerMethodField()

        class Meta:
            model = CandidateProfile
            fields = ['full_name', 'phone', 'resume_url']

        def get_resume_url(self, obj):
            if obj.current_resume:
                return obj.current_resume.file.url
            return None

class EmployerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = "__all__"
        read_only_fields = (
            "user",
            "is_verified",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        )
    def validate_company_domain(self, value):
        if value:
            domain_regex = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
            if not re.match(domain_regex, value):
                raise serializers.ValidationError(
                    "Enter a valid company domain (e.g., example.com)."
                )
        return value

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Company name cannot be empty."
            )
        return value

    def validate(self, attrs):
        
        request = self.context.get("request")
        if request and request.user.is_staff:
            required_fields = [
                attrs.get("company_name"),
                attrs.get("company_domain"),
                attrs.get("company_size"),
                attrs.get("industry"),
            ]
            if not all(required_fields):
                raise serializers.ValidationError(
                    "All company details are required for verification."
                )
        return attrs
    
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]
class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = CandidateProfile
        fields = [
            "id",
            "user",
            "experience_years",
            "education",
            "expected_salary",
            "current_location",
            "skills",
            "created_at",
        ]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

