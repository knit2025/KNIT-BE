# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Family(models.Model):
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='ACTIVE')

class User(AbstractUser):
    name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=30, blank=True)
    birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, default='MEMBER')
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name= 'users',null=True, blank=True)
