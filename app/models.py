from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class JobSeeker(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    qualification = models.CharField(max_length=500)
    cv = models.CharField(max_length=255,blank=True,null=True)
    cv_file = models.FileField(upload_to=f'cv/', blank=True, null=True)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    profile_image = models.ImageField(null=True, blank=True)


class Employeer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    company_name = models.CharField(max_length=100)
    country = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    company_size = models.IntegerField()
    logo = models.ImageField(null=True, blank=True)

class JobPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    job_description = models.TextField(max_length=500, blank=True, null=True)
    required_skills = models.TextField(max_length=500, blank=True, null=True)
    salary_range = models.IntegerField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    city=models.CharField(max_length=200)
    country=models.CharField(max_length=200)
    
    def __str__(self):
        return f"{self.id} - {self.job_title}"
    
class Applications(models.Model):
    
    class STATUS(models.TextChoices):
        Applied='Applied',_('Applied')
        Approved='Approved',_('Approved')
        Rejected='Rejected',_('Rejected')
        Hired='Hired',_('Hired')
    
    
    job_seeker = models.ForeignKey(User, on_delete=models.CASCADE)
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE) 
    created_at=models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,
        choices=STATUS.choices,
        default=STATUS.Applied,
    )

    def __str__(self):
        return f"{self.id}"
    
    
class Notifications(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.id} - {self.content}'