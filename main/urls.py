from django.urls import path
from .views import FamilyCharacterView, TodayPreviewView

app_name = 'home'

urlpatterns = [
    path('character/', FamilyCharacterView.as_view(), name='character'),
    path('today-question/', TodayPreviewView.as_view(), name='today_question'),
]
