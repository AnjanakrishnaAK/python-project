from django.db import models

# Create your models here.
from accounts.models import User
from accounts.models import EmployerProfile, CandidateProfile
from accounts.models import Skill, Resume

class Job(models.Model):
    employer = models.ForeignKey('accounts.User',
        
        on_delete=models.CASCADE,
        related_name='jobs'
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    location = models.CharField(max_length=255,null=True,blank=True,db_index=True)
    experience_min = models.IntegerField(default=0)
    experience_max = models.IntegerField(default=10)

    salary_min = models.IntegerField(default=0)
    salary_max = models.IntegerField(default=0)

    job_type = models.CharField(
        max_length=20,
        choices=(
            ('full_time', 'Full Time'),
            ('part_time', 'Part Time'),
            ('remote', 'Remote'),
            ('internship', 'Internship'),
        ),
        default='full_time',
        db_index=True
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="jobs"
    )

    status = models.CharField(
        max_length=20,
        choices=(
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('paused', 'Paused'),
            ('closed', 'Closed'),
        ),
        default='draft',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class JobApplication(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=(
            ('applied', 'Applied'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired'),
        ),
        default='applied'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'candidate')
        ordering = ['-applied_at']


class SavedJob(models.Model):

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_jobs"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("candidate", "job")