# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Family(models.Model):
    code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='ACTIVE')

    def __str__(self):
        return f'Family({self.id}, {self.code})'
    
class User(AbstractUser):
    name = models.CharField(max_length=30, blank=True)
    nickname = models.CharField(max_length=30, blank=True)
    birth = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=20, default='MEMBER')
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, related_name= 'users',null=True, blank=True)

    def __str__(self):
        return f'User({self.id}, {self.username}, {self.name})'