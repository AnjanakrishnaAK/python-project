from rest_framework import serializers
from .models import Application,ApplicationStatusHistory


class ApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company = serializers.CharField(
        source="job.company_name",
        read_only=True
    )

    class Meta:

        model = Application

        fields = [
            "id",
            "job",
            "job_title",
            "company",
            "status",
            "applied_at",
        ]

class TimelineSerializer(serializers.ModelSerializer):

    class Meta:
        model = ApplicationStatusHistory
        fields = "__all__"