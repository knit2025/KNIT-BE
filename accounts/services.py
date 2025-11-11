import string, random
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model, authenticate
from rest_framework import exceptions as drf_exc
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Family
from .selectors import *

User = get_user_model()

def generateCode(length=6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphabet, k=length))

#가족 새로 생성
def createFamilyAndCode() -> Family:
    code = generateCode()
    while Family.objects.filter(code=code).exists():
        code = generateCode()
    family = Family.objects.create(code=code, status = "ACTIVE" )
    return family

#유저 생성
def createUser(validated: dict) :
    password = validated.pop('password')
    familyCode = validated.pop('familyCode', None)

    family = isFamilyCodeExists(familyCode)
    if familyCode and family is None:
        raise drf_exc.ValidationError({'familyCode': '유효하지 않음'})

    try:
        user = User(**validated) 
        if family:
            user.family = family
        user.set_password(password)
        user.save() # user 만듦
        return user
    except IntegrityError:
        raise drf_exc.ValidationError({'loginId': '이미 사용 중인 아이디입니다.'})

#토큰 발급(로그인)
def loginUser(*, loginId:str, password:str) -> dict :
    user = authenticate(username = loginId, password = password)
    
    if user is None:
        raise drf_exc.ValidationError({'detail':'아이디 또는 비밀번호가 맞지 않습니다'})
    
    if not user.is_active:
        raise drf_exc.ValidationError({'detail': '비활성화된 계정입니다.'})

    refresh = RefreshToken.for_user(user)
    return {
        'user': user,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
