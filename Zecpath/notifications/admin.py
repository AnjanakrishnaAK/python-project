from django.contrib import admin
from .models import EmailDeliveryLog
# Register your models here.
@admin.register(EmailDeliveryLog)
class EmailDeliveryLogAdmin(admin.ModelAdmin):

    list_display = (
        "email",
        "subject",
        "status",
        "created_at"
    )

    search_fields = ("email", "subject")