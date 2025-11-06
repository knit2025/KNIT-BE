from django.shortcuts import render
from .models import Family, User
from .serializers import *
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import *
from .selectors import *

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginReqSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        loginId = serializer.validated_data['loginId']
        password = serializer.validated_data['password']

        result = loginUser(loginId=loginId, password=password)
        user = result['user']
        res = LoginResSerializer(user).data
        res['access'] = result['access']
        res['refresh'] = result['refresh']
        return Response(res, status=status.HTTP_200_OK)


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupReqSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = createUser(serializer.validated_data)

        result = loginUser(loginId=user.loginId, password=request.data['password'])
        res = SignupResSerializer(user).data
        res['access'] = result['access']
        res['refresh'] = result['refresh']
        return Response(res, status=status.HTTP_201_CREATED)


class FamilyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        family = createFamilyAndCode()
        res = FamilyCodeResSerializer(family).data
        return Response(res, status=status.HTTP_201_CREATED)


class LoginIdCheckView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        loginId = request.query_params.get('loginId')
        if not loginId:
            return Response(
                {"message": "loginId를 입력해주세요."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        check = isIdTaken(loginId)

        message = (
            {"message": "id is taken"}
            if check
            else {"message": "ok "}
        )
        return Response(message, status=status.HTTP_200_OK)
