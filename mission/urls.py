from django.urls import path
from .views import *

app_name = 'missions'

urlpatterns = [
    path('today', TodayMissionView.as_view(), name='todayMission'),
    path('completed', CompletedMissionsView.as_view(), name='completedMission'),
    path('', MissionDetailView.as_view(), name='missionDetail'),
    path('submit', MissionSubmitView.as_view(), name = 'missionSubmit')
]