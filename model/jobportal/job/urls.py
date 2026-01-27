from django.urls import path
from .views import home, users_list, jobs_list, applications_list

urlpatterns = [
    path('', home),
    path('users/', users_list),
    path('jobs/', jobs_list),
    path('applications/', applications_list),
]