from django.db import models

from django.utils import timezone
from django.conf import settings
from .managers import UserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):
        return f"{self.email} ({self.role})"

    

class Profile(models.Model):

    ROLE_CHOICES = (
        ("candidate", "Candidate"),
        ("employer", "Employer"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        default="candidate",
        choices=ROLE_CHOICES
    )

    skills = models.TextField(blank=True)

    location = models.CharField(
        max_length=255,
        blank=True
    )

    experience = models.IntegerField(default=0)

    def skill_list(self):
        if not self.skills:
            return []
        return [
            skill.strip().lower()
            for skill in self.skills.split(",")
        ]

    def __str__(self):
        return f"{self.user.username} Profile"

    
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
    class Meta:
        ordering = ["-created_at"]
    
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
        related_name="resumes"
    )

    file = models.FileField(upload_to="resumes/")
    is_active = models.BooleanField(default=False)

    parsed_data = models.JSONField(
        null=True,
        blank=True
    )

    is_parsed = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.user} Resume"


