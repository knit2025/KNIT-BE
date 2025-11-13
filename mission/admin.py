from django.contrib import admin
from .models import *

# Create your tests here.
admin.site.register(Mission)
admin.site.register(MissionInstance)
admin.site.register(MissionInstanceUser)