from django.contrib import admin
from .models import User,CandidateProfile, EmployerProfile

admin.site.register(User)
admin.site.register(CandidateProfile)
admin.site.register(EmployerProfile)