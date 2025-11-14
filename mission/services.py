from django.utils import timezone
from django.db import transaction
from .models import MissionInstance, MissionInstanceUser

#유저가 미션 소감 & 사진 제출 완료 
#가족이 미션 다 완료했으면 isCompleted True 로 수정
@transaction.atomic
def submitMission(missionInstanceId, user, opinion, image=None):
    try:
        missionInstance = MissionInstance.objects.select_related('family').get(
            id=missionInstanceId,
            family=user.family
        )
    except MissionInstance.DoesNotExist:
        raise ValueError("해당 미션을 찾을 수 없습니다.")
    
    if missionInstance.isCompleted:
        raise ValueError("이미 완료된 미션입니다.")
    
    # 유저의 제출 정보 생성 / 업데이트
    missionUser, created = MissionInstanceUser.objects.get_or_create(
        missionInstance=missionInstance,
        user=user,
        defaults={
            'opinion': opinion,
            'image': image,
            'isSubmitted': True
        }
    )
    
    if not created:
        missionUser.opinion = opinion
        if image:
            missionUser.image = image
        missionUser.isSubmitted = True
        missionUser.updatedAt = timezone.now().date()
        missionUser.save()
    
    # 가족의 모든 유저가 제출했는지 확인
    family = missionInstance.family
    family_users_count = family.users.count()
    submittedCount = MissionInstanceUser.objects.filter(
        missionInstance=missionInstance,
        isSubmitted=True
    ).count()
    
    # 모든 유저가 제출했으면 미션 완료(완료 시각 수정ㄴ)
    if submittedCount >= family_users_count:
        missionInstance.isCompleted = True
        missionInstance.completedDate = timezone.now().date()
        missionInstance.save()
    
    return missionUser