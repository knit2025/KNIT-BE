from django.contrib import admin
from .models import *

# Create your tests here.
admin.site.register(AdminQ)
admin.site.register(FamilyQuestionInstance)
admin.site.register(AdminQAnswer)