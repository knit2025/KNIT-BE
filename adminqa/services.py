from django.db import transaction
from rest_framework import exceptions as drf_exc
from .models import AdminQAnswer, FamilyQuestionInstance
from .selectors import get_current_instance_for_family
from accounts.models import Family
from .selectors import (
    get_current_instance_for_family, count_answers,
    count_distinct_family_members, has_user_answered
)

DEFAULT_REWARD_EXP = 10  

def _get_instance_for_user_or_404(user, instance_id: int | None):
    if instance_id:
        try:
            return FamilyQuestionInstance.objects.get(id=instance_id)
        except FamilyQuestionInstance.DoesNotExist:
            raise drf_exc.ValidationError({'detail': '해당 인스턴스가 없습니다.'})
    inst = get_current_instance_for_family(family=user.family)
    if not inst:
        raise drf_exc.ValidationError({'detail': '현재 진행 중인 가족 질문이 없습니다.'})
    return inst

@transaction.atomic
def create_answer_once(*, user, instance_id: int | None, content: str, is_anonymous: bool) -> AdminQAnswer:
    
    # 한 인스턴스당 사용자 1회만 답변 가능 (수정 제출 없음)
    # 최초 제출 시 가족 포인트 +1
    
    fqi = _get_instance_for_user_or_404(user, instance_id)

    # 가족 검증
    if fqi.family_id != getattr(user.family, 'id', None):
        raise drf_exc.ValidationError({'detail': '해당 가족의 질문만 답변할 수 있습니다.'})

    # 이미 답변했는지 확인
    if AdminQAnswer.objects.filter(family_q_instance=fqi, user=user).exists():
        raise drf_exc.ValidationError({'detail': '이미 답변했습니다.'})

    # 최초 생성
    answer = AdminQAnswer.objects.create(
        family_q_instance=fqi,
        user=user,
        content=content,
        is_anonymous=is_anonymous,
    )

    # 가족 포인트 +1
    fam: Family | None = getattr(user, 'family', None)
    if fam:
        fam.points = (fam.points or 0) + 1
        fam.save(update_fields=['points'])

    return answer


@transaction.atomic
def reward_if_all_answered(*, user) -> dict:
    fqi = _get_instance_for_user_or_404(user)
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