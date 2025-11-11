from django.db import models
from django.conf import settings # User 참조용
from django.db.models import Q

# Create your models here.

from accounts.models import Family # accounts 앱의 Family 모델 사용
User = settings.AUTH_USER_MODEL

class AdminQ(models.Model):
  # 관리자가 입력한 "오늘의 질문"
  text = models.TextField()
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-created_at'] # 최신순 기본 정렬
    verbose_name = 'Admin Question'
    verbose_name_plural = 'Admin Question'
    indexes = [
        models.Index(fields=['is_active', 'created_at']),
    ]

  def __str__(self):
    return self.text[:20]
  

class FamilyQuestionInstance(models.Model):
  #  가족 단위로 배정된 '오늘의 질문' 인스턴스

  STATUS_PENDING = 'PENDING'
  STATUS_CLOSED = 'CLOSED'
  STATUS_CHOICES = (
      (STATUS_PENDING, 'Pending'),
      (STATUS_CLOSED, 'Closed'),
  )


  family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='admin_q_instances')
  admin_q = models.ForeignKey(AdminQ, on_delete=models.CASCADE, related_name='family_instances')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING) # pending, closed 등
  is_current = models.BooleanField(default=True) # 현재 진행중인 질문인지 확인
  exp = models.IntegerField(default=0) # 보상, 경험치
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
      ordering = ['-created_at', '-id']
      indexes = [
          models.Index(fields=['family', 'is_current']),
          models.Index(fields=['admin_q', 'status']),
      ]
      # 한 가족은 동시에 current 인스턴스 1개만 허용
      constraints = [
        models.UniqueConstraint(
          fields=['family'],
          condition=Q(is_current=True),
          name='uq_family_current_adminq_instance',
        ),
      ]

  def __str__(self):
      return f'FQI#{self.id} fam={self.family_id} [{self.status}] current={self.is_current}'

class AdminQAnswer(models.Model):
  # 가족 질문 인스턴스에 대한 유저 답변
  family_q_instance = models.ForeignKey(FamilyQuestionInstance, on_delete=models.CASCADE, related_name='answers')
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_q_answers')
  content = models.TextField()
  is_anonymous = models.BooleanField(default=False)
  is_ancestral = models.BooleanField(default=False) # ERD의 imsAncestorId 용도 (필요하면 FK로 변경)
  
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ['-created_at', '-id']
    indexes = [
      models.Index(fields=['family_q_instance', 'user']),
      models.Index(fields=['created_at']),
    ]
    # 한 유저는 같은 인스턴스에 1회만 답변 (중복 제출 방지)
    constraints = [
      models.UniqueConstraint(
        fields=['family_q_instance', 'user'],
        name='uq_answer_per_user_per_instance',
      ),
    ]

  def __str__(self):
      return f'Ans#{self.id} inst={self.family_q_instance_id} user={self.user_id}'