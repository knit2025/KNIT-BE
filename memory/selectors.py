from django.contrib.auth import get_user_model
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from .models import Post
from accounts.models import *
from mission.models import *
from adminqa.models import *
from customqa.models import *

User = get_user_model()

#가족 구성원이 올린 Post 리스트
def getFamilyPosts(*, family, limit=50, offset=0):
    return Post.objects.filter(
        user__family=family
    ).select_related('user').order_by('-created_at', '-id')[offset:offset + limit]

#가족이 했던 미션 리스트
def getFamilyMissions(*, family, limit=50, offset=0):
    return MissionInstance.objects.filter(
        family=family,
        isCompleted=True
    ).select_related('mission').prefetch_related(
        'userMissions__user'
    ).order_by('-completedDate', '-id')[offset:offset + limit]


#답햇던 오늘의 질문 리스트 
def getFamilyAdminQuestions(*, family, limit=50, offset=0):
    return FamilyQuestionInstance.objects.filter(
        family=family,
        status=FamilyQuestionInstance.STATUS_CLOSED
    ).select_related('admin_q').order_by('-created_at', '-id')[offset:offset + limit]


#가족끼리 나눈 Custom QA(지금 필요없는거임)
def getFamilyCustomQuestions(*, family, limit=50, offset=0):
    return CustomQ.objects.filter(
        family=family
    ).select_related('from_user', 'to_user').order_by('-created_at', '-id')[offset:offset + limit]


def getAllMemories(*, family, limit=50, offset=0):
    """
    가족의 모든 추억을 최신순으로 정렬하여 반환
    - posts, missions, familyQuestionInstances를 합쳐서 정렬
    """
    posts = list(getFamilyPosts(family=family, limit=limit * 2))
    missions = list(getFamilyMissions(family=family, limit=limit * 2))
    fq_instances = list(getFamilyCustomQuestions(family=family, limit=limit * 2))
    
    # 모든 항목을 created_at 기준으로 정렬
    all_items = sorted(
        chain(posts, missions, fq_instances),
        key=attrgetter('created_at'),
        reverse=True
    )
    
    return all_items[offset:offset + limit]

#서브 함수
def countFamilyMemories(*, family):
    posts_count = Post.objects.filter(user__family=family).count()
    missions_count = MissionInstance.objects.filter(family=family).count()
    fq_instances_count = FamilyQuestionInstance.objects.filter(family=family).count()
    
    return {
        'posts': posts_count,
        'missions': missions_count,
        'familyQuestionInstances': fq_instances_count,
    }

#특정 게시물 조회
def getPostById(post_id: int):
    try:
        return Post.objects.select_related('user').get(id=post_id)
    except Post.DoesNotExist:
        return None