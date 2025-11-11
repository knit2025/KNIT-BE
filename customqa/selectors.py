from django.contrib.auth import get_user_model
from .models import CustomQ, CustomQAnswer

User = get_user_model()


def list_family_questions(*, family, limit=50, offset=0, to_me_only=False, me: User | None = None):
    qs = CustomQ.objects.filter(family=family).select_related('from_user', 'to_user')
    if to_me_only and me is not None:
        # 나에게 지정된 질문 또는 전체 대상(None)
        qs = qs.filter(to_user__in=[None, me])
    return qs.order_by('-created_at', '-id')[offset: offset + limit]


def get_question_or_none(qid: int):
    try:
        return CustomQ.objects.select_related('from_user', 'to_user', 'family').get(id=qid)
    except CustomQ.DoesNotExist:
        return None


def list_answers_for_question(question: CustomQ):
    return (CustomQAnswer.objects
            .filter(question=question)
            .select_related('user')
            .order_by('-created_at', '-id'))


def has_user_answered(question: CustomQ, user: User) -> bool:
    return CustomQAnswer.objects.filter(question=question, user=user).exists()
