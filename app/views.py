from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import CreateAPIView, UpdateAPIView,ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from .permissions import IsEmployer,IsJobseeker,JobPostPermissions,IsOwner,IsOwnerOrAdmin
from .models import JobSeeker, Employeer, JobPost,Applications, User,Notifications
from .serializers import JobSeekerSerializer, EmployeerSerializer, JobPostSerializerWithSalary, JobPostSerializerWithoutSalary,ApplyApplicationSerializer,UserOwnAppliedApplicationSerializer
from .serializers import ApplicationSerializer,NotificationSerializer,JobPostToggleSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import JobPostFilter
from .paginations import JobPostPagination
from user_auth.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser



class EmployeerGenericCreateUpdateApiView(CreateAPIView,UpdateAPIView):
    queryset = Employeer.objects.all()
    serializer_class = EmployeerSerializer
    permission_classes=[IsEmployer]
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs): # works before serializer validation

        if  Employeer.objects.filter(user=self.request.user).exists():
            
            return Response("already-created", status= status.HTTP_406_NOT_ACCEPTABLE)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer): 
        return Employeer.objects.create(user=self.request.user, **serializer.validated_data)



class JobSeekerGenericCreateUpdateApiView(CreateAPIView,UpdateAPIView):
    queryset = JobSeeker.objects.all()
    serializer_class = JobSeekerSerializer
    permission_classes=[IsJobseeker]
    parser_classes = (MultiPartParser,)

    def create(self, request, *args, **kwargs): 

        if  JobSeeker.objects.filter(user=self.request.user).exists():
            
            return Response("already-created", status= status.HTTP_406_NOT_ACCEPTABLE)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer): 
        return JobSeeker.objects.create(user=self.request.user, **serializer.validated_data)




class JobPostModelViewSet(ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializerWithSalary
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostFilter
    permission_classes=[JobPostPermissions]
    
    def get_serializer_class(self):
        if self.request.user.is_authenticated == False:
            return JobPostSerializerWithoutSalary
        else:
            return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action == "create":
            return [IsEmployer()]
        return super().get_permissions()
    
    
# each employeer can see only its own jobpost
    @action(detail=False, methods=["get"],permission_classes=[IsAuthenticated, IsEmployer])
    def my_jobposts(self, request):
        user = self.request.user
        queryset = JobPost.objects.filter(user=user)
        serializer = JobPostSerializerWithSalary(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['put'],serializer_class=JobPostToggleSerializer,permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def toggle(self,request,id):
        jobpost=JobPost.objects.filter(pk=id)
        jobpost.is_enabled=not jobpost.is_enabled
        jobpost.save(update_fields=['is_enabled'])
        return Response('Success') 
    
    
    
    @action(detail=True,methods=['post'],permission_classes=[IsAuthenticated,IsJobseeker],serializer_class=ApplyApplicationSerializer)
    def apply(self, request:Request, pk=None):
        
        jobpost = JobPost.objects.get(id=pk)
        
        my_applications=Applications.objects.filter(job_post=jobpost,job_seeker=self.request.user)
        
        if my_applications.exists():
            return Response("Already Applied", status=status.HTTP_406_NOT_ACCEPTABLE)
        
        applications=Applications.objects.create(job_post=jobpost,job_seeker=self.request.user)
        content=f'{self.request.user} has Applied for the job post \n {jobpost} \n Application ID={applications.id} '
        
        notifications_obj = {
            'user': jobpost.user.id,
            'content': content
        }
        not_serializer=NotificationSerializer(data=notifications_obj)
        if not_serializer.is_valid():
            not_serializer.save()
        
        return Response("Applied Successfully", status=status.HTTP_200_OK)
    
    
    
    
    @action(detail=False,methods=['get'],permission_classes=[IsAuthenticated, IsJobseeker])
    def my_applications(self,request):
        user=self.request.user
        queryset=Applications.objects.filter(job_seeker=user)
        serializer=UserOwnAppliedApplicationSerializer(queryset,many=True)
        return Response(serializer.data)
    
    @action(detail=True,methods=['get'],permission_classes=[IsOwnerOrAdmin, IsAuthenticated])
    def applicants(self,request,pk):
        job_post=JobPost.objects.get(pk=pk)
        
        if job_post.user != self.request.user:
            return Response("Unauthorized Access", status=status.HTTP_401_UNAUTHORIZED)
        
        queryset=Applications.objects.filter(job_post=job_post)
        users=User.objects.filter(id__in=queryset.values_list('job_seeker')).all()
        serializer=UserSerializer(users,many=True)
        return Response(serializer.data)
        

class UpdateApplicationStatusView(APIView):
    permission_classes=[IsAuthenticated,IsOwner]
    serializer_classes=ApplicationSerializer
    @swagger_auto_schema(request_body=ApplicationSerializer)
    def put(self, request, pk,applicant_id):
        
        try:
            job_post=JobPost.objects.get(id=pk,user=self.request.user)
        except JobPost.DoesNotExist:
            return Response("Post does not exist or Unauthorized Access", status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            job_seeker=User.objects.get(id=applicant_id)
        except User.DoesNotExist:
            return Response("User does not exist", status=status.HTTP_404_NOT_FOUND)
        
        try:
            application=Applications.objects.get(job_post=job_post,job_seeker=job_seeker)
        except:
            return Response("Application does not exist", status=status.HTTP_404_NOT_FOUND)
        
        application.status = request.data.get('status')
        application.save()
        notificaton_obj={
            "user":job_seeker.id,
            "content": f"Your application for {job_post} has been updated to {application.status}"
        }
        not_serializer=NotificationSerializer(data=notificaton_obj)
        if not_serializer.is_valid():
            not_serializer.save()

        return Response("Status updated successfully", status=status.HTTP_200_OK)
        
        
class NotificationsView(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=NotificationSerializer
    queryset=Notifications.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user).all()
    