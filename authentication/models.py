from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """扩展Django默认用户模型的用户配置文件"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    google_id = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.URLField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"