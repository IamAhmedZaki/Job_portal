from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsEmployer(BasePermission):
    def has_permission(self, request: Request, view):
        return request.user.groups.filter(name = 'Employer').exists()
    def has_object_permission(self, request: Request, view, obj):
        return request.user.groups.filter(name = 'Employer').exists()
    
class IsJobseeker(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name="JobSeeker").exists():
            return True
        return False
    
class JobPostPermissions(BasePermission):
    def has_permission(self, request: Request, view):
        if request.method == 'GET':
            return True
        if request.user.groups.filter(name = 'Employer').exists() or request.user.is_superuser:
            return True
        else:
            return False
        
class IsOwner(BasePermission):
    def has_permission(self, request: Request, view):
        return request.user.groups.filter(name = 'Employer').exists() or request.user.is_superuser
    
    def has_object_permission(self, request: Request, view, obj):
        return obj.job_post.user.id == request.user.id
    
class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request: Request, view):
        return request.user.groups.filter(name = 'Employer').exists() or request.user.is_superuser
    
    def has_object_permission(self, request: Request, view, obj):
        if request.method in ('GET', 'DELETE'):
            return obj.job_post.user.id == request.user.id or request.user.is_superuser
        return obj.job_post.user.id == request.user.id

    
    