from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Post
from adminqa.models import *
from mission.serializers import *

User = get_user_model()


# Post 관련
class PostCreateReqSerializer(serializers.Serializer):
    text = serializers.CharField()
    image = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    date = serializers.DateField()


class PostResSerializer(serializers.ModelSerializer):
    postId = serializers.IntegerField(source='id', read_only=True)
    userId = serializers.IntegerField(source='user_id', read_only=True)
    text = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    date = serializers.DateField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)

    class Meta:
        model = Post
        fields = [
            'postId', 'userId', 'username', 'nickname',
            'text', 'image', 'date', 'createdAt'
        ]


# FamilyQuestionInstance 간소화
class MemoryFQInstanceResSerializer(serializers.ModelSerializer):
    instanceId = serializers.IntegerField(source='id', read_only=True)
    adminQId = serializers.IntegerField(source='admin_q_id', read_only=True)
    isCurrent = serializers.BooleanField(source='is_current')
    status = serializers.CharField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    familyId = serializers.IntegerField(source='family_id', read_only=True)
    
    # 질문 텍스트 포함
    text = serializers.CharField(source='admin_q.text', read_only=True)

    class Meta:
        model = FamilyQuestionInstance
        fields = [
            'instanceId', 'adminQId', 'text',
            'isCurrent', 'status', 'createdAt', 'familyId'
        ]


# 통합 추억 응답
class MemoriesResSerializer(serializers.Serializer):
    counts = serializers.DictField()
    posts = PostResSerializer(many=True)
    missions = MissionDetailResSerializer(many=True)
    familyQuestionInstances = MemoryFQInstanceResSerializer(many=True)


# 항목별
class FilteredMemoriesResSerializer(serializers.Serializer):
    type = serializers.CharField()  # 'post', 'mission', 'familyQuestion'
    items = serializers.ListField()
    total = serializers.IntegerField()