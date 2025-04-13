from django.contrib import admin
from .models import Community, JoinRequest

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'name', 'type', 'created_at']
    list_filter = ['type']
    search_fields = ['code', 'name']

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'department_name', 'course_number', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['department_name', 'course_number']
