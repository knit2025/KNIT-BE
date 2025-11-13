from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model

from .serializers import (
    CustomQCreateReqSerializer, CustomQResSerializer,
    CustomQAnswerReqSerializer, CustomQAnswerResSerializer
)
from .selectors import (
    list_family_questions, get_question_or_none, list_answers_for_question, has_user_answered
)
from .services import create_question, create_or_update_answer
from accounts.models import *

User = get_user_model()


class CreateQuestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomQCreateReqSerializer

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)

        if not request.user.family:
            return Response({'detail': '가족이 없습니다.'}, status=400)
        
        family = request.user.family
        role = ser.validated_data['toUser']
        try:
            toUser = User.objects.get(family=family, role=role)
            to_user_id = toUser.id
        except User.DoesNotExist:
            return Response({'detail': '해당 역할의 사용자를 찾을 수 없습니다.'}, status=400)

        q = create_question(
            user=request.user,
            text=ser.validated_data['text'],
            to_user_id=to_user_id
            
        )
        return Response(CustomQResSerializer(q).data, status=201)


class ListQuestionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.family:
            return Response({'detail': '가족이 없습니다.'}, status=400)

        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        to_me_only = request.query_params.get('toMe', 'false').lower() == 'true'

        qs = list_family_questions(
            family=request.user.family,
            limit=limit,
            offset=offset,
            to_me_only=to_me_only,
            me=request.user
        )
        data = CustomQResSerializer(qs, many=True).data
        return Response(data, status=200)


class CreateAnswerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomQAnswerReqSerializer

    def post(self, request, customq_id: int):
        q = get_question_or_none(customq_id)
        if not q:
            return Response({'detail': '질문이 없습니다.'}, status=404)

        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)

        ans = create_or_update_answer(
            user=request.user,
            custom_q=q,
            content=ser.validated_data['content'],
            is_anonymous=ser.validated_data.get('isAnonymous', False)
        )
        return Response(CustomQAnswerResSerializer(ans).data, status=201)


class ListAnswersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, customq_id: int):
        q = get_question_or_none(customq_id)
        if not q:
            return Response({'detail': '질문이 없습니다.'}, status=404)

        # 가족 검증(다른 가족 질문 열람 제한)
        if not request.user.family or request.user.family_id != q.family_id:
            return Response({'detail': '다른 가족의 질문입니다.'}, status=403)

        answers = list_answers_for_question(q)
        data = CustomQAnswerResSerializer(answers, many=True).data

        # 내 답변 여부 플래그 추가(헤더 수준 메타로)
        my_answered = has_user_answered(q, request.user)
        return Response({'items': data, 'myAnswered': my_answered}, status=200)
