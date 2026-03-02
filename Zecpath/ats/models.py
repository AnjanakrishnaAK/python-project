from django.db import models

# Create your models here.
from jobs.models import Job
from accounts.models import CandidateProfile


class ATSScore(models.Model):

    candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.CASCADE,
        related_name="ats_scores"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="ats_scores"
    )

    skills_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    education_score = models.FloatField(default=0)

    total_score = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["candidate", "job"]
        ordering = ["-total_score"]

    def __str__(self):
        return f"{self.candidate} - {self.job} ({self.total_score}%)"