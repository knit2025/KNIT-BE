from django.db import models
from django.conf import settings
from accounts.models import Family

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField()
    image = models.CharField(max_length=500, blank=True, null=True)  # 이미지 URL 또는 경로
    date = models.DateField()  
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['date']),
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self):
        return f'Post#{self.id} user={self.user_id} {self.text[:20]}'