from django.urls import path
from .views import TodayQuestionView, CreateAnswerView, InstanceAnswersListView, FamilyPointsView

app_name = 'adminqa'

urlpatterns = [
    path('today/', TodayQuestionView.as_view(), name='today'),
    path('answer/', CreateAnswerView.as_view(), name='answer'),
    path('<int:instance_id>/answers/', InstanceAnswersListView.as_view(), name='answers_list'),
    path('family/points/', FamilyPointsView.as_view(), name='family_points'),
]