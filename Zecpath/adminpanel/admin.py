from django.contrib import admin

# Register your models here.

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "admin",
        "action",
        "target_user",
        "target_job_id",
        "created_at",
    )

    search_fields = ("admin__username", "action")

    list_filter = ("action", "created_at")