from django.contrib.auth import get_user_model
from .models import CustomQ, CustomQAnswer
from django.db.models import Q

User = get_user_model()


def list_family_questions(*, family, limit=50, offset=0, to_me_only=False, me: User | None = None):
    qs = CustomQ.objects.filter(family=family).select_related('from_user', 'to_user')
    
    if me is not None:
        qs = qs.filter(
            Q(is_public=True) |  
            Q(from_user=me) |     
            Q(to_user=me)        
        )
    else:
        # 로그인하지 않은 경우 공개 질문만
        qs = qs.filter(is_public=True)
    
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

def can_view_question(question: CustomQ, user: User) -> bool:

    # 같은 가족인지 확인
    if not user.family or question.family_id != user.family_id:
        return False
    
    # 공개 질문이면 OK
    if question.is_public:
        return True
    
    # 비공개 질문: 작성자 또는 수신자만 가능
    return question.from_user_id == user.id or question.to_user_id == user.id