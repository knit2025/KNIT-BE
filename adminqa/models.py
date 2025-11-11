from django.db import models
from django.conf import settings # User 참조용


# Create your models here.

User = settings.AUTH_USER_MODEL

class AdminQ(models.Model):
  # 관리자 지정 질문
  text = models.TextField()
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.text[:20]
  

class FamilyQuestionInstance(models.Model):
  #  가족 단위로 배정된 오늘의 질문 인스턴스
  family = models.ForeignKey('accounts.Family', on_delete=models.CASCADE, related_name='admin_q_instances')
  admin_q = models.ForeignKey(AdminQ, on_delete=models.CASCADE, related_name='family_instances')
  status = models.CharField(max_length=20, default='pending') # pending, closed 등
  is_current = models.BooleanField(default=True) # 현재 진행중인 질문인지 확인
  exp = models.IntegerField(default=0) # 보상, 경험치
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
      indexes = [
          models.Index(fields=['family', 'is_current']),
      ]

class AdminQAnswer(models.Model):
  # 가족 질문에 대한 유저 답변
  family_q_instance = models.ForeignKey(FamilyQuestionInstance, on_delete=models.CASCADE, related_name='answers')
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_q_answers')
  content = models.TextField()
  is_anonymous = models.BooleanField(default=False)
  is_ancestral = models.BooleanField(default=False) # ERD의 imsAncestorId 용도 (필요하면 FK로 변경)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['family_q_instance', 'user'])]