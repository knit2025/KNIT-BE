from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('signup', SignupView.as_view(), name='signup'),
    path('checkId', LoginIdCheckView.as_view(), name='check_id'),
    path('login', LoginView.as_view(), name='login'),
    path('code', FamilyCodeView.as_view(), name = 'familyCode')
]