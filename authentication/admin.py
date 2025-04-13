from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# 如果需要自定义用户模型的管理界面，可以在这里注册
# admin.site.register(CustomUser, CustomUserAdmin)