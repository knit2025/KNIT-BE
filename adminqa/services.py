from django.db import transaction
from rest_framework import exceptions as drf_exc
from .models import AdminQAnswer, FamilyQuestionInstance
from .selectors import (
    get_current_instance_for_family, count_answers,
    count_distinct_family_members, has_user_answered
)

DEFAULT_REWARD_EXP = 10  # ERD 상 exp는 FamilyQuestionInstance에 보관

def get_today_instance_for_user(user) -> FamilyQuestionInstance:
    fqi = get_current_instance_for_family(family=user.family)
    if not fqi:
        raise drf_exc.ValidationError({'detail': '현재 진행 중인 가족 질문이 없습니다.'})
    return fqi

@transaction.atomic
def create_or_update_answer(*, user, instance_id: int | None, content: str, is_anonymous: bool) -> AdminQAnswer:
    if instance_id:
        fqi = FamilyQuestionInstance.objects.select_for_update().get(id=instance_id)
    else:
        fqi = get_today_instance_for_user(user)

    if fqi.family_id != getattr(user.family, 'id', None):
        raise drf_exc.ValidationError({'detail': '해당 가족 질문이 아닙니다.'})

    answer, created = AdminQAnswer.objects.get_or_create(
        family_q_instance=fqi,
        user=user,
        defaults={'content': content, 'is_anonymous': is_anonymous}
    )
    if not created:
        answer.content = content
        answer.is_anonymous = is_anonymous
        answer.save(update_fields=['content', 'is_anonymous', 'updated_at'])
    return answer

@transaction.atomic
def reward_if_all_answered(*, user) -> dict:
    fqi = get_today_instance_for_user(user)
    family = user.family
    total_members = count_distinct_family_members(family)
    answered = count_answers(fqi)

    if answered < total_members:
        return {'rewarded': False, 'reason': 'not_all_answered', 'answered': answered, 'total': total_members}

    # 이미 보상됐는지 간단하게 확인 - exp가 0 초과면 보상 완료로 간주(원하는 방식에 따라 변경 가능)
    if fqi.exp and fqi.exp > 0:
        return {'rewarded': False, 'reason': 'already_rewarded'}

    fqi.exp = (fqi.exp or 0) + DEFAULT_REWARD_EXP
    fqi.save(update_fields=['exp'])
    return {'rewarded': True, 'points': DEFAULT_REWARD_EXP}
