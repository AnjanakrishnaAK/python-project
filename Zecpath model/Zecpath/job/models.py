from django.db import models
from django.contrib.auth.models import User




class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)
    company_description = models.TextField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.company_name




class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField()
    experience = models.PositiveIntegerField(help_text="Years of experience")
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.user.username




class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.title




class Application(models.Model):
    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired'),
    ]


    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ('candidate', 'job')


    def __str__(self):
        return f"{self.candidate} - {self.job}"