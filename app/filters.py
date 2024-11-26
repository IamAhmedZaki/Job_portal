from django_filters import rest_framework as filters
from .models import JobPost

class JobPostFilter(filters.FilterSet):
    class Meta:
        model = JobPost
        fields = ['city', 'country', 'job_title']
