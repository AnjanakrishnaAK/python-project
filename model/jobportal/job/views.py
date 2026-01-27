

# Create your views here.
from django.http import JsonResponse
from .models import User, Job, Application

def home(request):
    return JsonResponse({"message": "Job Portal Backend Running"})


def users_list(request):
    users = list(User.objects.values())
    return JsonResponse(users, safe=False)


def jobs_list(request):
    jobs = list(Job.objects.values())
    return JsonResponse(jobs, safe=False)


def applications_list(request):
    applications = Application.objects.select_related('user', 'job')
    data = []

    for app in applications:
        data.append({
            "user": app.user.name,
            "job": app.job.title,
            "applied_at": app.applied_at
        })

    return JsonResponse(data, safe=False)