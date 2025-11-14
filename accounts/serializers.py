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
    role = serializers.CharField(max_length=30)
    nickname = serializers.CharField(max_length=30)
    familyCode = serializers.CharField(max_length=20)

class SignupResSerializer(serializers.Serializer):
    loginId = serializers.CharField(source='username')
    name = serializers.CharField()
    birth = serializers.DateField()
    role = serializers.CharField()
    nickname = serializers.CharField()
    familyCode = serializers.SerializerMethodField()
    
    def get_familyCode(self, obj):
        return obj.family.code if obj.family else None

#가족코드 생성
class FamilyCodeResSerializer(serializers.Serializer):
    familyId = serializers.IntegerField(source='id')
    familyCode = serializers.CharField(max_length=20, source='code')
    status = serializers.CharField(max_length=20)
    createdAt = serializers.DateTimeField(source='created_at')
    
#로그인
class LoginReqSerializer(serializers.Serializer):
    loginId = serializers.CharField(max_length=150, source='username')
    password = serializers.CharField(write_only=True)

class LoginResSerializer(serializers.Serializer):
    loginId = serializers.CharField(source='username', read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'nickname', 'role', 'birth']

class FamilyResSerializer(serializers.ModelSerializer):
    users = UserSimpleSerializer(many=True, read_only=True)   # ← 추가 포인트

    class Meta:
        model = Family
        fields = ['id', 'code', 'created_at', 'status', 'points', 'users']