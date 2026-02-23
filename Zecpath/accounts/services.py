import hashlib
from django.db import transaction
from django.db.models import Max
from .models import Resume


from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework import serializers
from .models import Profile,Resume






class AuthService:
    @staticmethod
    def login(email, password):
        user = authenticate(email=email, password=password)
        if not user:
            raise Exception("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role,
        }

    @staticmethod
    def logout(refresh_token):
        RefreshToken(refresh_token).blacklist()

def calculate_file_hash(file):
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()


@transaction.atomic
def upload_or_replace_resume(profile, file):
    file_hash = calculate_file_hash(file)

    last_version = (
        Resume.objects
        .filter(candidate=profile)
        .aggregate(max_version=Max('version'))
        ['max_version'] or 0
    )

    Resume.objects.filter(
        candidate=profile,
        is_active=True
    ).update(is_active=False)


    resume = Resume.objects.create(
        candidate=profile,
        file=file,
        file_hash=file_hash,
        version=last_version + 1,
        is_active=True
    )

   
    profile.current_resume = resume
    profile.save(update_fields=['current_resume'])

    return resume

class ResumeService:

    @staticmethod
    def upload_resume(user, file):
        if user.role != "candidate":
            raise PermissionDenied("Only candidates can upload resumes")

        return Resume.objects.create(
            candidate=user,
            file=file
        )

    @staticmethod
    def list_resumes(user):
        if user.role != "candidate":
            raise PermissionDenied("Only candidates can view resumes")

        return Resume.objects.filter(candidate=user)
    
class ProfileService:
    @staticmethod
    def get_profile(user):
        return Profile.objects.get(user=user)

    @staticmethod
    def update_profile(user, data):
        profile = Profile.objects.get(user=user)
        profile.name = data.get("name", profile.name)
        profile.bio = data.get("bio", profile.bio)
        profile.save()
        return profile
    

        
    
class ResumeService:
    @staticmethod
    def upload(user, file):
        if file.content_type != "application/pdf":
            raise ValidationError("Only PDF allowed")

        if file.size > 2 * 1024 * 1024:
            raise ValidationError("Max file size is 2MB")

        return Resume.objects.create(
            candidate=user,
            file=file
        )