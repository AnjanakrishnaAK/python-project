from rest_framework import serializers
from jobs.models import JobApplication,Job,JobApplication,JobApplication
from rest_framework import serializers
from accounts.models import Resume
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import Job, SavedJob

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job',
            'resume',
            'cover_letter',
            'status',
            'applied_at',
        ]
        read_only_fields = ['status', 'applied_at']

class EmployerJobApplicationSerializer(serializers.ModelSerializer):
    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True
    )

    candidate_name = serializers.CharField(
        source="candidate.user.email",
        read_only=True
    )

    resume_url = serializers.FileField(
        source="resume.file",
        read_only=True
    )

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'candidate_email',
            'candidate_name',
            'resume_url',
            'status',
            'applied_at',
        ]

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        exclude = [
            'employer',
            'status',
            'is_verified',
            'is_archived',
            'created_at',
            'updated_at',
        ]

class JobUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        exclude = [
            'employer',
            'is_verified',
            'is_archived',
            'created_at',
            'updated_at',
        ]

class PublicJobSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    skills = serializers.StringRelatedField(many=True)

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'description',
            'employer_name',
            'skills',
            'created_at'
        ]

class EmployerJobSerializer(serializers.ModelSerializer):
    applications_count = serializers.IntegerField(
        source='applications.count',
        read_only=True
    )

    class Meta:
        model = Job
        fields = '__all__'


class ApplyJobSerializer(serializers.Serializer):
    job_id = serializers.IntegerField()
    resume_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context['request']
        user = request.user

     
        if not hasattr(user, "candidateprofile"):
            raise serializers.ValidationError("Only candidates can apply.")

        candidate = user.candidateprofile

       
        try:
            job = Job.objects.get(id=data['job_id'], status='active')
        except Job.DoesNotExist:
            raise serializers.ValidationError("Job not available.")

     
        if job.employer.user == user:
            raise serializers.ValidationError("You cannot apply to your own job.")

      
        if JobApplication.objects.filter(job=job, candidate=candidate).exists():
            raise serializers.ValidationError("You already applied to this job.")

      
        try:
            resume = Resume.objects.get(
                id=data['resume_id'],
                candidate=candidate
            )
        except Resume.DoesNotExist:
            raise serializers.ValidationError("Invalid resume selected.")

        data['job'] = job
        data['candidate'] = candidate
        data['resume'] = resume

        return data
    

class CandidateApplicationRecordSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    company = serializers.CharField(source='job.employer.company_name', read_only=True)
    location = serializers.CharField(source='job.location', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job_title',
            'company',
            'location',
            'status',
            'applied_at'
        ]

class CandidateApplicationRecordsAPIView(ListAPIView):
    serializer_class = CandidateApplicationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, "candidateprofile"):
            return JobApplication.objects.none()

        return JobApplication.objects.select_related(
            'job',
            'job__employer'
        ).filter(
            candidate=user.candidateprofile
        ).order_by('-applied_at')
    

class EmployerApplicationRecordSerializer(serializers.ModelSerializer):
    candidate_email = serializers.CharField(
        source='candidate.user.email',
        read_only=True
    )
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job_title',
            'candidate_email',
            'status',
            'applied_at'
        ]

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class SavedJobSerializer(serializers.ModelSerializer):

    job = JobSerializer()

    class Meta:

        model = SavedJob

        fields = ["id", "job", "saved_at"]