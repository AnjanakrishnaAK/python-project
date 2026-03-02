from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):

    admin_email = serializers.EmailField(
        source="admin.email",
        read_only=True
    )

    target_user_email = serializers.EmailField(
        source="target_user.email",
        read_only=True
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "description",
            "admin_email",
            "target_user_email",
            "target_job_id",
            "ip_address",
            "created_at",
        ]