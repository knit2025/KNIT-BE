from django.contrib.auth import get_user_model
from .models import Family,User

User = get_user_model()

def isIdTaken(loginId: str) -> bool :
    return User.objects.filter(username = loginId).exists()

def isFamilyCodeExists(code:str) :
    if not code :
        return None
    try:
        return Family.objects.get(code=code, status = "ACTIVE")
    except Family.DoesNotExist:
        return None
    