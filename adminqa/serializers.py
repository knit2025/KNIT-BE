from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import AdminQ, FamilyQuestionInstance, AdminQAnswer

User = get_user_model()


# AdminQ (오늘의 질문)
class AdminQResSerializer(serializers.ModelSerializer):
    adminQId = serializers.IntegerField(source='id', read_only=True)
    text = serializers.CharField()

    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    isActive = serializers.BooleanField(source='is_active')

    class Meta:
        model = AdminQ
        fields = ['adminQId', 'text', 'isActive', 'createdAt']


# FamilyQuestionInstance (진행하고 있는 오늘의 질문)
class FamilyQuestionInstanceResSerializer(serializers.ModelSerializer):
    instanceId = serializers.IntegerField(source='id', read_only=True)
    familyId = serializers.IntegerField(source='family_id', read_only=True)
    adminQId = serializers.IntegerField(source='admin_q_id', read_only=True)

    status = serializers.CharField()
    isCurrent = serializers.BooleanField(source='is_current')
    exp = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    # 질문 본문(text) 포함
    text = serializers.CharField(source='admin_q.text', read_only=True)

    class Meta:
        model = FamilyQuestionInstance
        fields = [
            'instanceId', 'familyId', 'adminQId',
            'text', 'status', 'isCurrent', 'exp', 'createdAt'
        ]


# /adminq/today 응답 전용 (진행 중 인스턴스 + 추가정보)
class TodayInstanceResSerializer(FamilyQuestionInstanceResSerializer):
    
    # 진행 중 인스턴스 조회 시, 내 답변 여부/답변 수 등을 함께 내려주기 위한 응답 전용
    myAnswered = serializers.BooleanField(read_only=True)
    totalAnswers = serializers.IntegerField(read_only=True)

    class Meta(FamilyQuestionInstanceResSerializer.Meta):
        fields = FamilyQuestionInstanceResSerializer.Meta.fields + [
            'myAnswered', 'totalAnswers'
        ]


# AdminQAnswer (유저 답변)
class AdminQAnswerReqSerializer(serializers.Serializer):
    # POST /adminq/answer 요청

    instanceId = serializers.IntegerField() # FamilyQuestionInstance id
    content = serializers.CharField()
    isAnonymous = serializers.BooleanField(default=False)


class AdminQAnswerResSerializer(serializers.ModelSerializer):
    #단일/목록 응답 공용
    # 익명일 경우 displayName을 '익명'으로 내려줌
    answerId = serializers.IntegerField(source='id', read_only=True)
    instanceId = serializers.IntegerField(source='family_q_instance_id', read_only=True)
    userId = serializers.IntegerField(source='user_id', read_only=True)

    content = serializers.CharField()
    isAnonymous = serializers.BooleanField(source='is_anonymous')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    # 편의 필드
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    displayName = serializers.SerializerMethodField()

    def get_displayName(self, obj: AdminQAnswer) -> str:
        if obj.is_anonymous:
            return '익명'
        # 닉네임 우선, 없으면 username
        return getattr(obj.user, 'nickname', None) or getattr(obj.user, 'username', '')

    class Meta:
        model = AdminQAnswer
        fields = [
            'answerId', 'instanceId', 'userId',
            'username', 'nickname', 'displayName',
            'content', 'isAnonymous', 'createdAt', 'updatedAt'
        ]


# 가족 포인트 적립 결과 응답
class FamilyRewardResSerializer(serializers.Serializer):
    # POST /adminq/family/points 결과 포맷을 통일하기 위한 간단 응답
    rewarded = serializers.BooleanField()
    points = serializers.IntegerField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_null=True)
    answered = serializers.IntegerField(required=False, allow_null=True)
    total = serializers.IntegerField(required=False, allow_null=True)

# adminq/serializers.py (기존 코드에 추가)

# AdminQ 상세 응답 전용 Serializer
class AdminQDetailResSerializer(serializers.ModelSerializer):
    instanceId = serializers.IntegerField(source='id', read_only=True)
    familyId = serializers.IntegerField(source='family_id', read_only=True)
    adminQId = serializers.IntegerField(source='admin_q_id', read_only=True)
    
    text = serializers.CharField(source='admin_q.text', read_only=True)
    status = serializers.CharField()
    isCurrent = serializers.BooleanField(source='is_current')
    exp = serializers.IntegerField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    # 추가 정보
    myAnswered = serializers.BooleanField(read_only=True)
    totalAnswers = serializers.IntegerField(read_only=True)
    
    # 답변 목록
    answers = AdminQAnswerResSerializer(many=True, read_only=True)
    
    class Meta:
        model = FamilyQuestionInstance
        fields = [
            'instanceId', 'familyId', 'adminQId',
            'text', 'status', 'isCurrent', 'exp', 'createdAt',
            'myAnswered', 'totalAnswers', 'answers'
        ]