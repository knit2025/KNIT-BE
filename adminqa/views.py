from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    AdminQAnswerReqSerializer, AdminQAnswerResSerializer,
    TodayInstanceResSerializer
)
from .selectors import (
    get_instance_by_id, list_answers_for_instance,
    has_user_answered, count_answers, get_current_instance_for_family
)
from .services import create_or_update_answer, reward_if_all_answered, create_answer_once #수정된서비스로 교체

class TodayQuestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fqi = get_current_instance_for_family(family=request.user.family)
        if not fqi:
            return Response({'detail': '현재 진행 중인 가족 질문이 없습니다.'}, status=404)

        data = TodayInstanceResSerializer(fqi).data
        data['myAnswered'] = has_user_answered(fqi, request.user)
        data['totalAnswers'] = count_answers(fqi)
        return Response(data, status=200)


class CreateAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AdminQAnswerReqSerializer

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        answer = create_answer_once(
            user=request.user,
            instance_id=ser.validated_data.get('instanceId'),
            content=ser.validated_data['content'],
            is_anonymous=ser.validated_data.get('isAnonymous', False)
        )
        return Response(AdminQAnswerResSerializer(answer).data, status=201)


class InstanceAnswersListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, instance_id: int):
        fqi = get_instance_by_id(instance_id)
        if not fqi:
            return Response({'detail': '해당 인스턴스가 없습니다.'}, status=404)
        answers = list_answers_for_instance(fqi)
        return Response(AdminQAnswerResSerializer(answers, many=True).data, status=200)


class FamilyPointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        result = reward_if_all_answered(user=request.user)
        # 보상 안 됐으면 202(accepted)로 전달
        return Response(result, status=200 if result.get('rewarded') else 202)
