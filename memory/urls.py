from django.urls import path
from .views import *

app_name = 'memory'

urlpatterns = [
    path('', MemoriesView.as_view(), name='all-memories'),
    path('filter', FilteredMemoriesView.as_view(), name='filtered-memories'),
    path('post', CreatePostView.as_view(), name='create-post'),
    path('post/<int:postId>', PostDetailView.as_view(), name='post-detail'),
]