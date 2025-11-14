from django.utils import timezone
from .models import Mission, MissionInstance, MissionInstanceUser

#하루에 미션 하나씩
def getTodayMission(family):
    
    # 부여된 미션 중 완료되지 않은 미션 찾기
    incompleteMission = MissionInstance.objects.filter(family=family,isCompleted=False
    ).select_related('mission').first()
    
    if incompleteMission:
        return incompleteMission
    
    #만약에 다 부여된 미션을 다 완료했다면 가족이 아직 받지 않은 미션 중 하나를 랜덤으로
    completedMissionIds = MissionInstance.objects.filter(
        family=family,
        isCompleted=True
    ).values_list('mission_id', flat=True)
    
    available_mission = Mission.objects.exclude(id__in=completedMissionIds).first()
    
    # 모든 미션을 완료했다면 첫 번째 미션부터 다시 (일단 이렇게 해둠)
    if not available_mission:
        available_mission = Mission.objects.first()
    
    if available_mission:
        new_mission_instance = MissionInstance.objects.create(
            mission=available_mission,
            family=family
        )
        return (
            MissionInstance.objects
            .select_related('mission')
            .prefetch_related('userMissions__user')
            .get(pk=new_mission_instance.pk)
        )
    
    return None

#완료한 미션 리스트(완료된 날짜순으로 반환)
def getCompletedMissions(family):
    return MissionInstance.objects.filter(family=family,isCompleted=True).select_related('mission').order_by('-completedDate')

#특정 미션의 상세정보(mission title, content , 각 유저의 소감, 이미지 다 FK 키로 한번에)
def getMissionDetail(missionInstanceId, family):
    try:
        mission_instance = MissionInstance.objects.select_related('mission').prefetch_related(
            'userMissions__user'
        ).get(id=missionInstanceId,family=family,isCompleted=True)
        return mission_instance
    except MissionInstance.DoesNotExist:
        return None

#각 유저가 미션 제출햇는지 
def getUserMissionSubmission(mission_instance, user):
    try:
        return MissionInstanceUser.objects.get(missionInstance=mission_instance,user=user)
    except MissionInstanceUser.DoesNotExist:
        return None