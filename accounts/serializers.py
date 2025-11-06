from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import *

User = get_user_model()

#회원가입
class SignupReqSerializer(serializers.Serializer):
    loginId = serializers.CharField(max_length=150, source='username')
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=30)
    birth = serializers.DateField(required=False, allow_null=True)
    role = serializers.CharField(max_lenth=30)
    nickname = serializers.CharField(max_lenth=30)
    familyCode = serializers.CharField(max_lenth=20)

class SignipResSerializer(serializers.Serializer):
    loginId = serializers.CharField(max_length=150, source='username')
    familyCode = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'loginId', 'name', 'birth', 'role', 'nickname', 'familyCode', 'date_joined')
        read_only_fields = fields

    def get_familyCode(self, obj):
        return getattr(getattr(obj, 'family', None), 'code', None)

#가족코드 생성
class FamilyCodeResSerializer(serializers.Serializer):
    familyId = serializers.IntegerField()
    familyCode = serializers.CharField(max_length = 20)
    status = serializers.CharField(max_length = 20)
    createdAt = serializers.DateTimeField()
    
#로그인
class LoginReqSerializer(serializers.Serializer):
    loginId = serializers.CharField(max_length=150, source='username')
    password = serializers.CharField(write_only=True)
