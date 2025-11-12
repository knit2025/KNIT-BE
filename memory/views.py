from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import *
from .selectors import *
from .services import *

#모든 추억들 다 조회
class MemoriesView(APIView):
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.family:
            return Response({'detail': '가족이 없습니다.'}, status=400)

        family = request.user.family
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))


        # 개수
        counts = countFamilyMemories(family=family)

        data = {
            'counts': counts,
            'posts': PostResSerializer(many=True).data,
            'missions': MemoryMissionResSerializer(many=True).data,
            'familyQuestionInstances': MemoryFQInstanceResSerializer(many=True).data,
        }

        return Response(data, status=200)

#특정 타입만 조회
class FilteredMemoriesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.family:
            return Response({'detail': '가족이 없습니다.'}, status=400)

        family = request.user.family
        memoryType = request.query_params.get('type', 'post')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))

        if memoryType == 'post':
            items = getFamilyPosts(family=family, limit=limit, offset=offset)
            serialized = PostResSerializer(items, many=True).data
        elif memoryType == 'mission':
            items = getFamilyMissions(family=family, limit=limit, offset=offset)
            serialized = MemoryMissionResSerializer(items, many=True).data
        elif memoryType == 'familyQuestion':
            items = getFamilyAdminQuestions(family=family, limit=limit, offset=offset)
            serialized = MemoryFQInstanceResSerializer(items, many=True).data
        else:
            return Response({'detail': '잘못된 타입입니다. (post, mission, familyQuestion)'}, status=400)

        data = {
            'type': memoryType,
            'items': serialized,
            'total': len(serialized)
        }

        return Response(data, status=200)


class CreatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostCreateReqSerializer

    def post(self, request):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)

        post = createPost(
            user=request.user,
            text=ser.validated_data['text'],
            image=ser.validated_data.get('image'),
            postDate=ser.validated_data['date']
        )

        return Response(PostResSerializer(post).data, status=201)


class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, postId: int):
        post = getPostById(postId)
        if not post:
            return Response({'detail': '게시글이 없습니다.'}, status=404)

        # 같은 가족인지 확인
        if not request.user.family or post.user.family_id != request.user.family_id:
            return Response({'detail': '다른 가족의 게시글입니다.'}, status=403)

        return Response(PostResSerializer(post).data, status=200)

    def patch(self, request, postId: int):
        post = getPostById(postId)
        if not post:
            return Response({'detail': '게시글이 없습니다.'}, status=404)

        ser = PostCreateReqSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        
        newText = ser.validated_data.get('text', post.text)
        newImage = ser.validated_data.get('image', post.image)
        newDate = ser.validated_data.get('date', post.postDate)

        # 서비스 레이어가 전체 업데이트만 받는다면 기존 값 채워서 호출
        updatedPost = updatePost(
            post=post,
            user=request.user,
            text=newText,
            image=newImage,
            postDate=newDate,
        )

        return Response(PostResSerializer(updatedPost).data, status=200)

    def delete(self, request, postId: int):
        post = getPostById(postId)
        if not post:
            return Response({'detail': '게시글이 없습니다.'}, status=404)

        deletePost(post=post, user=request.user)
        return Response({'detail': '삭제되었습니다.'}, status=204)


