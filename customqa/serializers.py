from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CustomQ, CustomQAnswer

User = get_user_model()


# 질문 (CustomQ)
class CustomQCreateReqSerializer(serializers.Serializer):
    text = serializers.CharField()
    isAnonymous = serializers.BooleanField()
    isPublic = serializers.BooleanField()
    toUser = serializers.CharField()


class CustomQResSerializer(serializers.ModelSerializer):
    customQId = serializers.IntegerField(source='id', read_only=True)
    familyId = serializers.IntegerField(source='family_id', read_only=True)
    fromUserId = serializers.IntegerField(source='from_user_id', read_only=True)
    toUserId = serializers.IntegerField(source='to_user_id', read_only=True, allow_null=True)

    text = serializers.CharField()
    isAnonymous = serializers.BooleanField(source='is_anonymous', read_only=True)
    isPublic = serializers.BooleanField(source='is_public', read_only=True)s
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    fromUsername = serializers.CharField(source='from_user.username', read_only=True)
    toUsername = serializers.CharField(source='to_user.username', read_only=True, allow_null=True)
    
    displayFromName = serializers.SerializerMethodField()

    def get_displayFromName(self, obj: CustomQ) -> str:
        if obj.is_anonymous:
            return '익명'
        return getattr(obj.from_user, 'nickname', None) or getattr(obj.from_user, 'username', '')

    class Meta:
        model = CustomQ
        fields = [
            'customQId', 'familyId',
            'fromUserId', 'fromUsername',
            'toUserId', 'toUsername',
            'text', 'createdAt'
        ]


# 답변 (CustomQAnswer)
class CustomQAnswerReqSerializer(serializers.Serializer):
    content = serializers.CharField()
    isAnonymous = serializers.BooleanField(default=False)


class CustomQAnswerResSerializer(serializers.ModelSerializer):
    answerId = serializers.IntegerField(source='id', read_only=True)
    customQId = serializers.IntegerField(source='question_id', read_only=True)
    userId = serializers.IntegerField(source='user_id', read_only=True)

    content = serializers.CharField()
    isAnonymous = serializers.BooleanField(source='is_anonymous')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    username = serializers.CharField(source='user.username', read_only=True)
    nickname = serializers.CharField(source='user.nickname', read_only=True)
    displayName = serializers.SerializerMethodField()

    def get_displayName(self, obj: CustomQAnswer) -> str:
        if obj.is_anonymous:
            return '익명'
        return getattr(obj.user, 'nickname', None) or getattr(obj.user, 'username', '')

    class Meta:
        model = CustomQAnswer
        fields = [
            'answerId', 'customQId', 'userId',
            'username', 'nickname', 'displayName',
            'content', 'isAnonymous', 'createdAt', 'updatedAt'
        ]
