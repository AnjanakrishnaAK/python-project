from django.contrib import admin

# Register your models here.
from .models import Employer, Candidate, Job, Application


admin.site.register(Employer)
admin.site.register(Candidate)
admin.site.register(Job)
admin.site.register(Application)