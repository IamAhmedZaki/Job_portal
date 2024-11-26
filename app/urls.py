from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmployeerGenericCreateUpdateApiView, JobPostModelViewSet, JobSeekerGenericCreateUpdateApiView,UpdateApplicationStatusView
from .views import NotificationsView

router = DefaultRouter()
router.register("job-post", JobPostModelViewSet)

urlpatterns = [
    path('employeer/profile/', EmployeerGenericCreateUpdateApiView.as_view()),
    path('jobSeeker/profile/', JobSeekerGenericCreateUpdateApiView.as_view()),
    path('job-post/<int:pk>/applicants/<int:applicant_id>/status', UpdateApplicationStatusView.as_view(), name='UpdateApplicantStatus'),
    path('notifications/', NotificationsView.as_view()),

] + router.urls

