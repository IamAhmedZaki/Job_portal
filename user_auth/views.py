from django.shortcuts import render
from rest_framework.permissions import AllowAny,IsAuthenticated

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import login, logout, authenticate
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, SignupSerializer, LoginSerializer,ChangePasswordSerializer,PasswordResetRequestSerializer,PasswordResetSerializer


@api_view(['POST'])
@swagger_auto_schema(request_body=SignupSerializer)
def signup_view(request : Request):
    data = request.data
    serializer = SignupSerializer(data=data)
    if serializer.is_valid():
        data = serializer.validated_data
        data['password'] = make_password(data['password'])
        # data['is_staff'] = 1
        # data['is_superuser'] = 1
        User.objects.create(**data)
    else:
        return Response("invalid data", status=status.HTTP_400_BAD_REQUEST)
    return Response("success")




@api_view(['POST'])

@swagger_auto_schema(request_body=LoginSerializer)
def login_view(request:Request):
    data = request.data
    serializer = LoginSerializer(data=data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        user = authenticate(request, username=data['username'], password=data['password'])
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else: 
           return Response("login credentials given were wrong", status=status.HTTP_400_BAD_REQUEST)
    else: 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request: Request):
    logout(request)
    return Response("log out!!!!!!")


@api_view(['GET'])
def profile_view(request: Request):
    if request.user.is_authenticated:
        user = UserSerializer(request.user)
        return Response(user.data)
    else:
        return Response("please login")
    
    
    
    
class ChangePasswordAPI(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ChangePasswordSerializer
    
    @swagger_auto_schema(request_body=ChangePasswordSerializer)    
    def put(self,request):
        try:
            data=request.data
            
            serializer=ChangePasswordSerializer(data=data)
            
            if serializer.is_valid():
                
                data1=serializer.data
                if data1['new_password'] != data1['confirm_password']:
                    return Response("error:new password and confirm password not same")
                
                
                
                auth=authenticate(username=request.user.username,password=data['old_password'])
                if not auth:
                    return Response("error:old password not correct")
                
                data1['new_password'] = make_password(data1['new_password'])
                
                request.user.password=data1['new_password']
                
                request.user.save()
                
                return Response("success:password changed")
                
            return Response({"error23":serializer.errors},status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error23": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
                

class PasswordResetRequestView(APIView):
    permission_classes=[IsAuthenticated]
    
    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            reset_link = f"http://127.0.0.1:8000/auth/reset-password/"
            email_body = f"Reset Link: {reset_link}"

            send_mail(
                "Password Reset Request",
                email_body,
                "mahmedzaki670@gmail.com",
                [email],
            )

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class PasswordResetView(APIView):
    
    permission_classes=[IsAuthenticated]
    serializer_class=PasswordResetSerializer
    
    @swagger_auto_schema(request_body=PasswordResetSerializer)
    def put(self,request):
        try:
            data=request.data
            
            serializer=PasswordResetSerializer(data=data)
            
            if serializer.is_valid():
                
                data1=serializer.validated_data
                
                
                
                
                data1['new_password'] = make_password(data1['new_password'])
                
                request.user.password=data1['new_password']
                
                

                
                request.user.save()
                
                return Response("success:password changed")
                
            return Response({"error23":serializer.errors},status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error23": str(e)}, status=status.HTTP_400_BAD_REQUEST)
