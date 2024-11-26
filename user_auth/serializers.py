from rest_framework import serializers
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from enum import Enum
class StatusEnum(Enum):
    JOB_SEEKER = "JobSeeker"
    EMPLOYEER = "Employeer"
   

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email=serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[(tag, tag.value) for tag in StatusEnum], read_only=True)
    

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    date_joined = serializers.DateTimeField(read_only=True) 


class ChangePasswordSerializer(serializers.Serializer):
    
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    old_password = serializers.CharField(write_only=True)
    
    
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value
    
    
class PasswordResetSerializer(serializers.Serializer):
    
    new_password = serializers.CharField(write_only=True)

    
        
