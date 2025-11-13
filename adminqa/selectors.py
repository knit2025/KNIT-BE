from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import AdminQ, FamilyQuestionInstance, AdminQAnswer

User = get_user_model()

def get_current_instance_for_family(*, family) -> FamilyQuestionInstance | None:
    if not family:
        return None
    return FamilyQuestionInstance.objects.filter(
        family=family, is_current=True
    ).select_related('admin_q').order_by('-created_at').first()

def get_instance_by_id(instance_id: int) -> FamilyQuestionInstance | None:
    try:
        return FamilyQuestionInstance.objects.select_related('admin_q', 'family').get(id=instance_id)
    except FamilyQuestionInstance.DoesNotExist:
        return None

def list_answers_for_instance(instance: FamilyQuestionInstance):
    return (AdminQAnswer.objects
            .filter(family_q_instance=instance)
            .select_related('user')
            .order_by('-created_at', '-id'))

def has_user_answered(instance: FamilyQuestionInstance, user: User) -> bool:
    return AdminQAnswer.objects.filter(family_q_instance=instance, user=user).exists()

def count_answers(instance: FamilyQuestionInstance) -> int:
    return AdminQAnswer.objects.filter(family_q_instance=instance).count()

def count_distinct_family_members(family) -> int:
    return User.objects.filter(family=family, is_active=True).count()

def get_instance_detail(*, instance_id: int, family) -> FamilyQuestionInstance | None:
    try:
        return FamilyQuestionInstance.objects.select_related(
            'admin_q', 'family'
        ).prefetch_related(
            'answers__user'  # 답변과 답변 작성자 미리 로드
        ).get(
            id=instance_id,
            family=family
        )
    except FamilyQuestionInstance.DoesNotExist:
        return None