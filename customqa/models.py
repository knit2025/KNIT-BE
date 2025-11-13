from django.db import models

# Create your models here.
from django.conf import settings
from accounts.models import Family

User = settings.AUTH_USER_MODEL


class CustomQ(models.Model):
    # 커스텀 질문 카드
    # ERD - customQId, txt, createdAt, toUser(FK), fromUser(FK), familyId
    
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='custom_questions')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_questions_created')
    to_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='custom_questions_received',
        help_text='지정 대상(선택). None이면 가족 전체 대상'
    )

    text = models.TextField()
    is_anonymous = models.BooleanField(default=False, help_text='질문자 익명 여부')
    is_public = models.BooleanField(default=True, help_text='질문 공개 여부')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['family', 'created_at']),
            models.Index(fields=['to_user']),
        ]
        verbose_name = 'Custom Question'
        verbose_name_plural = 'Custom Questions'

    def __str__(self):
        return f'CQ#{self.id} fam={self.family_id} {self.text[:18]}'


class CustomQAnswer(models.Model):
    # 커스텀 질문에 대한 유저 답변
    # ERD - customQAnswerId, content, createdAt, updatedAt, isAnonymous, customQId
    
    question = models.ForeignKey(
        CustomQ, on_delete=models.CASCADE, related_name='answers'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='customq_answers'
    )

    content = models.TextField()
    #is_anonymous = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['question', 'user']),
            models.Index(fields=['created_at']),
        ]
        # 동일 질문에 대한 동일 유저의 중복 답변 방지(정책 - 1인 1답)
        constraints = [
            models.UniqueConstraint(
                fields=['question', 'user'],
                name='uq_answer_per_user_per_customq',
            ),
        ]

    def __str__(self):
        return f'CQA#{self.id} q={self.question_id} user={self.user_id}'


class Reply(models.Model):
    # 커스텀 답변에 대한 댓글
    # ERD - replyId, customQAnswerId
    # 이번 스펙의 API에는 아직 사용되지 않지만, 확장 대비 최소 정의
    
    answer = models.ForeignKey(CustomQAnswer, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customq_replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']
        indexes = [
            models.Index(fields=['answer', 'created_at']),
        ]

    def __str__(self):
        return f'Reply#{self.id} ans={self.answer_id}'
