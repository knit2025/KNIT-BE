from django.urls import path
from .views import CreateQuestionView, ListQuestionsView, CreateAnswerView, ListAnswersView

app_name = 'customqa'

urlpatterns = [
    path('create/', CreateQuestionView.as_view(), name='create'),
    path('list/', ListQuestionsView.as_view(), name='list'),
    path('<int:customq_id>/answer/', CreateAnswerView.as_view(), name='answer'),
    path('<int:customq_id>/answers/', ListAnswersView.as_view(), name='answers'),
]