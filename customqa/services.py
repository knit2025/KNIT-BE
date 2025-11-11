from rest_framework import exceptions as drf_exc
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import CustomQ, CustomQAnswer

User = get_user_model()


def _validate_same_family(*, me: User, target: User | None):
    if target is None:
        return
    if not me.family or not target.family or me.family_id != target.family_id:
        raise drf_exc.ValidationError({'detail': '서로 다른 가족 구성원입니다.'})


@transaction.atomic
def create_question(*, user: User, text: str, to_user_id: int | None = None) -> CustomQ:
    if not user.family:
        raise drf_exc.ValidationError({'detail': '가족이 없는 사용자입니다.'})

    to_user = None
    if to_user_id is not None:
        try:
            to_user = User.objects.get(id=to_user_id, is_active=True)
        except User.DoesNotExist:
            raise drf_exc.ValidationError({'toUserId': '존재하지 않는 사용자입니다.'})
        _validate_same_family(me=user, target=to_user)

    q = CustomQ.objects.create(
        family=user.family,
        from_user=user,
        to_user=to_user,
        text=text
    )
    return q


@transaction.atomic
def create_or_update_answer(*, user: User, custom_q: CustomQ, content: str, is_anonymous: bool) -> CustomQAnswer:
    # 가족 일치 검증
    if not user.family or custom_q.family_id != user.family_id:
        raise drf_exc.ValidationError({'detail': '다른 가족의 질문에는 답할 수 없습니다.'})

    # 지정 대상(to_user)이 있는 경우, 해당 사용자만 답변 가능
    if custom_q.to_user_id and custom_q.to_user_id != user.id:
        raise drf_exc.ValidationError({'detail': '이 질문은 지정된 사용자만 답변할 수 있습니다.'})

    ans, created = CustomQAnswer.objects.get_or_create(
        question=custom_q,
        user=user,
        defaults={'content': content, 'is_anonymous': is_anonymous}
    )
    if not created:
        ans.content = content
        ans.is_anonymous = is_anonymous
        ans.save(update_fields=['content', 'is_anonymous', 'updated_at'])
    return ans
