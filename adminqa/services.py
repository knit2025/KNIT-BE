from django.db import transaction
from django.utils import timezone
from rest_framework import exceptions as drf_exc
from .models import AdminQ, AdminQAnswer, FamilyQuestionInstance
from .selectors import get_current_instance_for_family
from accounts.models import Family
from .selectors import (
    get_current_instance_for_family, count_answers,
    count_distinct_family_members, has_user_answered
)

DEFAULT_REWARD_EXP = 10  


# 오늘의 질문: 가족 기준으로 "오늘자 인스턴스"를 가져오거나, 없으면 생성
@transaction.atomic
def get_or_create_today_instance_for_family(*, family) -> FamilyQuestionInstance | None:
    
    # family가 없으면 None 반환
    # 오늘(created_at 날짜 기준)에 생성된 인스턴스가 있으면 그대로 사용
    # 없으면 AdminQ 템플릿에서 하나 선택해 새 인스턴스를 생성
    # 하루에 하나씩만 생성되도록 보장 (created_at__date 필터)
    
    if not family:
        return None

    today = timezone.localdate()

    # 1) 오늘자 인스턴스가 이미 있는지 확인
    qs_today = (FamilyQuestionInstance.objects
                .filter(family=family, created_at__date=today)
                .select_related('admin_q')
                .order_by('-created_at', '-id'))
    instance = qs_today.first()
    if instance:
        # 오늘자 인스턴스가 있으면 그걸 current로 맞춰주고 반환
        if not instance.is_current:
            FamilyQuestionInstance.objects.filter(
                family=family,
                is_current=True
            ).exclude(id=instance.id).update(is_current=False)
            instance.is_current = True
            instance.save(update_fields=['is_current'])
        return instance

    # 2) 오늘자 인스턴스가 없다면 새로 생성
    # (AdminQ 템플릿 중 ACTIVE인 것들만 대상으로 순차 선택)
    active_qs = AdminQ.objects.filter(is_active=True).order_by('id')
    if not active_qs.exists():
        # 쓰일 질문이 하나도 없으면 None 반환 (클라이언트에서 404로 변환 가능)
        return None

    # 지금까지 이 가족에게 발급된 인스턴스 개수
    total_instances = FamilyQuestionInstance.objects.filter(family=family).count()
    idx = total_instances % active_qs.count()
    admin_q = active_qs[idx]

    # 이전 current 인스턴스들 해제
    FamilyQuestionInstance.objects.filter(
        family=family,
        is_current=True,
    ).update(is_current=False)

    # 새 인스턴스 생성 (status/exp는 기존 정책 유지)
    instance = FamilyQuestionInstance.objects.create(
        family=family,
        admin_q=admin_q,
        status=FamilyQuestionInstance.STATUS_PENDING,
        is_current=True,
        exp=0,  # 필요하면 DEFAULT_REWARD_EXP 등으로 조정 가능
    )

    return instance


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