from django.db import models

# Create your models here.
from django.conf import settings


class AuditLog(models.Model):
    """
    Stores all admin actions for audit and tracking
    """

    ACTION_CHOICES = (
        ("APPROVE_EMPLOYER", "Approve Employer"),
        ("BLOCK_USER", "Block User"),
        ("UNBLOCK_USER", "Unblock User"),
        ("DELETE_JOB", "Delete Job"),
        ("REMOVE_SPAM_JOB", "Remove Spam Job"),
        ("FLAG_USER", "Flag User"),
        ("FLAG_JOB", "Flag Job"),
        ("APPROVE_JOB", "Approve Job"),
        ("DISABLE_JOB", "Disable Job"),
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="performed_actions"
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="affected_actions"
    )

    target_job_id = models.IntegerField(
        null=True,
        blank=True
    )

    description = models.TextField()

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.admin.username} - {self.action} - {self.created_at}"