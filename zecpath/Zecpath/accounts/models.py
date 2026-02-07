from django.db import models

from django.utils import timezone
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    objects = UserManager() 
    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    
    # Role for candidate / recruiter / admin
    ADMIN = 'ADMIN'
    EMPLOYER = 'EMPLOYER'
    CANDIDATE = 'CANDIDATE'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (EMPLOYER, 'Employer'),
        (CANDIDATE, 'Candidate'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CANDIDATE)

    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'       # login with email
    REQUIRED_FIELDS = ['username']  # username is required

    def __str__(self):
        return self.email
    
class BaseProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s"
    )
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    
class CandidateProfile(BaseProfile):
    skills = models.ManyToManyField(Skill, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    education = models.TextField(blank=True)
    expected_salary = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    current_resume = models.ForeignKey(
        'Resume',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_profile'
    )
    current_location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"CandidateProfile - {self.user}"
    
class EmployerProfile(BaseProfile):
    COMPANY_SIZE_CHOICES = [
        ("startup", "Startup"),
        ("sme", "SME"),
        ("enterprise", "Enterprise"),
    ]

    company_name = models.CharField(max_length=255)
    company_domain = models.CharField(max_length=255,null=True,blank=True)
    company_size = models.CharField(max_length=20,choices=COMPANY_SIZE_CHOICES,null=True,blank=True)
    industry = models.CharField(max_length=100,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    verification_docs = models.FileField(
        upload_to="zecpath/verification/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.company_name
    

class Resume(models.Model):
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    file = models.FileField(upload_to='resumes/')
    file_hash = models.CharField(max_length=64)
    version = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.user.email} - v{self.version}"