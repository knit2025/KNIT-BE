from django.db import transaction
from rest_framework import exceptions as drf_exc
from django.contrib.auth import get_user_model
from datetime import date

from .models import Post

User = get_user_model()


@transaction.atomic
def createPost(*, user: User, text: str, image: str | None, postDate: date) -> Post:
    if not user.family:
        raise drf_exc.ValidationError({'detail': '가족이 없는 사용자입니다.'})
    
    post = Post.objects.create(
        user=user,
        text=text,
        image=image,
        date=postDate
    )
    return post


@transaction.atomic
def updatePost(*, post: Post, user: User, text: str | None = None, image: str | None = None, postDate: date | None = None) -> Post:
    if post.user_id != user.id:
        raise drf_exc.ValidationError({'detail': '본인의 게시글만 수정할 수 있습니다.'})
    
    if text is not None:
        post.text = text
    if image is not None:
        post.image = image
    if postDate is not None:
        post.date = postDate
    
    post.save(update_fields=['text', 'image', 'date'])
    return post


@transaction.atomic
def deletePost(*, post: Post, user: User) -> None:
    if post.user_id != user.id:
        raise drf_exc.ValidationError({'detail': '본인의 게시글만 삭제할 수 있습니다.'})
    
    post.delete()