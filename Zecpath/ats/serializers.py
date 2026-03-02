from rest_framework import serializers
from ats.models import ATSScore


class ATSScoreSerializer(serializers.ModelSerializer):

    candidate_name = serializers.CharField(
        source="candidate.user.get_full_name",
        read_only=True
    )

    class Meta:
        model = ATSScore
        fields = [
            "id",
            "candidate",
            "candidate_name",
            "job",
            "skills_score",
            "experience_score",
            "education_score",
            "total_score",
        ]