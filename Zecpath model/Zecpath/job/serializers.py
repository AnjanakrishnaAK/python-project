from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Employer, Candidate, Job, Application




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']




class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)


    class Meta:
        model = Employer
        fields = '__all__'




class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)


    class Meta:
        model = Candidate
        fields = '__all__'




class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'




class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'