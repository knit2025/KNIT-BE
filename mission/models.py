from django.conf import settings
from django.db import models
from accounts.models import Family, User

# Create your models here.
class Mission(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f"[Mission] {self.title}"
    
class MissionInstance(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="instances")
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="missionInstances")
    text = models.TextField(null = True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    completedDate = models.DateField(null=True, blank=True)
    isCompleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["-completedDate"]
        

    
class MissionInstanceUser(models.Model):
    missionInstance = models.ForeignKey(MissionInstance, on_delete=models.CASCADE, related_name="userMissions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userMissionInstances")
    opinion = models.TextField(blank=True)
    image = models.ImageField(null = True, blank=True, upload_to="missions/")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isSubmitted = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
        models.UniqueConstraint(
            fields=["missionInstance", "user"],
            name="uqMissionInstanceUser",
        )
    ]
        
    def __str__(self):
        return f"[MI:{self.mission_instance_id}] User:{self.user_id} submitted={self.is_submitted}"