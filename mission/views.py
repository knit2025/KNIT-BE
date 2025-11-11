from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .selectors import *
from .services import *
from .serializers import *


class TodayMissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not getattr(user, "family", None):
            return Response(
                {"error": "가족에 속해있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        missionInstance = getTodayMission(user.family)

        if not missionInstance:
            return Response(
                {"error": "미션을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TodayMissionResSerializer(missionInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompletedMissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not getattr(user, "family", None):
            return Response(
                {"error": "가족에 속해있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        completedMissions = getCompletedMissions(user.family)
        serializer = CompletedMissionListResSerializer(completedMissions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MissionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not getattr(user, "family", None):
            return Response(
                {"error": "가족에 속해있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        missionId = request.query_params.get("missionId")
        if not missionId:
            return Response(
                {"error": "missionId 쿼리 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            missionInstanceId = int(missionId)
        except ValueError:
            return Response(
                {"error": "missionId는 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        missionInstance = getMissionDetail(
            missionInstanceId=missionInstanceId,
            family=user.family,
        )

        if not missionInstance:
            return Response(
                {"error": "완료된 미션을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MissionDetailResSerializer(missionInstance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MissionSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not getattr(user, "family", None):
            return Response(
                {"error": "가족에 속해있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reqSerializer = MissionSubmitReqSerializer(data=request.data)

        if not reqSerializer.is_valid():
            return Response(
                reqSerializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            missionUser = submitMission(
                missionInstanceId=reqSerializer.validated_data["missionInstanceId"],
                user=user,
                opinion=reqSerializer.validated_data["opinion"],
                image=reqSerializer.validated_data.get("image"),
            )

            return Response(
                {
                    "message": "미션 제출이 완료되었습니다.",
                    "isCompleted": missionUser.missionInstance.isCompleted,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
