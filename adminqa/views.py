from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .selectors import *
from .services import reward_if_all_answered, create_answer_once #수정된서비스로 교체

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

class QuestionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not getattr(user, "family", None):
            return Response(
                {"error": "가족에 속해있지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # 쿼리 파라미터로 instanceId 받기
        instance_id_param = request.query_params.get("adminqId")
        if not instance_id_param:
            return Response(
                {"error": "adminqId 쿼리 파라미터가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            instance_id = int(instance_id_param)
        except ValueError:
            return Response(
                {"error": "instanceId는 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 인스턴스 조회 (가족 검증 포함)
        instance = get_instance_detail(
            instance_id=instance_id,
            family=user.family
        )
        
        if not instance:
            return Response(
                {"error": "해당 질문을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = AdminQDetailResSerializer(instance)
        data = serializer.data
        
        # 내 답변 여부와 전체 답변 수 추가
        data['myAnswered'] = has_user_answered(instance, user)
        data['totalAnswers'] = count_answers(instance)
        
        return Response(data, status=status.HTTP_200_OK)