from rest_framework import serializers
from .models import *

#가족 미션 확인용 시리얼라이저
class MissionInstanceUserResSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source='user_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = MissionInstanceUser
        fields = [
            'userId', 'username', 'nickname',
            'isSubmitted', 'opinion', 'image',
            'createdAt', 'updatedAt',
        ]


# 오늘의 질문 반환
class TodayMissionResSerializer(serializers.Serializer):
    missionId = serializers.IntegerField(source='mission_id')
    missionInstanceId = serializers.IntegerField(source='id')
    title = serializers.CharField(source='mission.title')
    content = serializers.CharField(source='mission.content')
    isCompleted = serializers.BooleanField()
    userMissions = MissionInstanceUserResSerializer(many=True, read_only=True)


    def get_allSubmitted(self, obj):
        user_missions = obj.userMissions.all()
        if not user_missions.exists():
            return False
        return all(um.isSubmitted for um in user_missions)

# 완료된 미션 목록 반환
class CompletedMissionListResSerializer(serializers.Serializer):
    missionInstanceId = serializers.IntegerField(source='id')
    title = serializers.CharField(source='mission.title')
    content = serializers.CharField(source='mission.content')
    completedDate = serializers.DateField()

# 미션 완료 요청 (유저별 소감 및 사진 등록)
class MissionSubmitReqSerializer(serializers.Serializer):
    missionInstanceId = serializers.IntegerField()
    opinion = serializers.CharField()
    image = serializers.ImageField(required=False)

# 완료된 미션 상세 정보 - 유저별 정보
class MissionUserInfoSerializer(serializers.Serializer):
    userId = serializers.IntegerField(source='user_id')
    userName = serializers.CharField(source='user.name')
    opinion = serializers.CharField()
    image = serializers.ImageField(required=False)
    createdAt = serializers.DateTimeField()

# 완료된 미션 상세 정보 전체
class MissionDetailResSerializer(serializers.Serializer):
    missionInstanceId = serializers.IntegerField(source='id')
    title = serializers.CharField(source='mission.title')
    content = serializers.CharField(source='mission.content')
    completedDate = serializers.DateField()
    userSubmissions = MissionUserInfoSerializer(many=True, source='userMissions')