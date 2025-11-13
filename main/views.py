from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Family
from .services import compute_character_progress
from .serializers import CharacterProgressResSerializer
from adminqa.selectors import get_current_instance_for_family
from adminqa.serializers import TodayInstanceResSerializer
from adminqa.selectors import has_user_answered, count_answers  # 이미 구현돼 있다면 사용

class FamilyCharacterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fam = getattr(request.user, 'family', None)
        if not fam:
            return Response({'detail': '가족이 없습니다.'}, status=404)

        calc = compute_character_progress(fam.points or 0)
        data = {
            'familyId': fam.id,
            'familyCode': fam.code,
            **calc
        }
        return Response(CharacterProgressResSerializer(data).data, status=200)


class TodayPreviewView(APIView):
    
    # 홈 상단 말풍선 - 오늘의 질문 미리보기
    # 진행 중 인스턴스 + 내 답변 여부/총 답변 수
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        instance = get_current_instance_for_family(family=request.user.family)
        if not instance:
            return Response({'detail': '현재 진행 중인 가족 질문이 없습니다.'}, status=404)

        payload = TodayInstanceResSerializer(instance).data
        # 선택: 필요하면 myAnswered/totalAnswers도 붙여서 미리보기 강화 가능
        try:
            from adminqa.selectors import has_user_answered, count_answers
            payload['myAnswered'] = has_user_answered(instance, request.user)
            payload['totalAnswers'] = count_answers(instance)
        except Exception:
            pass
        return Response(payload, status=200)
