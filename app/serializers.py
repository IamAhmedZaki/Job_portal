from .models import JobSeeker, Employeer, JobPost
from rest_framework import serializers
from user_auth.serializers import UserSerializer
from .models import Applications,Notifications

from enum import Enum
class StatusEnum(Enum):
    ENABLE="enable"
    DISABLE="disable"

class JobSeekerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    dob = serializers.DateField(format="%Y-%m-%d") 
    class Meta:
        model = JobSeeker 
        fields = "__all__" 

class EmployeerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    dob = serializers.DateField(format="%Y-%m-%d") 
    class Meta:
        model = Employeer 
        fields = "__all__" 
        

class JobPostToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = ['id','is_enabled']



class JobPostSerializerWithSalary(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    

    class Meta:
        model =  JobPost
        fields = "__all__" 

    def create(self, validated_data):
        return JobPost.objects.create(**validated_data, user=self.context["request"].user)
    
class JobPostSerializerWithoutSalary(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    status = serializers.ChoiceField(choices=[(tag, tag.value) for tag in StatusEnum], read_only=True)
    class Meta:
        model =  JobPost
        fields = ["job_title", "job_description", "required_skills", "status", "user",'city','country']
        

        


class UserOwnAppliedApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applications
        fields = '__all__'


class JobApplyApplicationSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializerWithSalary(read_only=True)
    job_seeker_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Applications
        fields = '__all__'
        read_only_fields = [
                'status'
            ]
        
class ApplyApplicationSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializerWithSalary(read_only=True)
    job_seeker = JobSeekerSerializer(read_only=True)

    class Meta:
        model = Applications
        fields = '__all__'
        extra_kwargs = {
            'job_post': {'read_only': True},
        }
        read_only_fields = [
            'status'
        ]

            
            
        
class ApplicationSerializer(serializers.ModelSerializer):
    job_post = JobPostSerializerWithSalary(read_only=True)
    job_seeker = JobSeekerSerializer(read_only=True)

    class Meta:
        model = Applications
        fields = '__all__'
        extra_kwargs = {
            'job_post': {'read_only': True},
        }

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'