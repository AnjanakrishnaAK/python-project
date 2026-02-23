import django_filters
from .models import Job
class JobFilter(django_filters.FilterSet):
    min_experience = django_filters.NumberFilter(
        field_name='experience_min',
        lookup_expr='gte'
    )
    max_experience = django_filters.NumberFilter(
        field_name='experience_max',
        lookup_expr='lte'
    )
    min_salary = django_filters.NumberFilter(
        field_name='salary_min',
        lookup_expr='gte'
    )
    max_salary = django_filters.NumberFilter(
        field_name='salary_max',
        lookup_expr='lte'
    )
    location = django_filters.CharFilter(
        field_name='location',
        lookup_expr='icontains'
    )
    job_type = django_filters.CharFilter(
        field_name='job_type',
        lookup_expr='exact'
    )
    skill = django_filters.CharFilter(
        field_name='skills__name',
        lookup_expr='icontains'
    )
    class Meta:
        model = Job
        fields = []