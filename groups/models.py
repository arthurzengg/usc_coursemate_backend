from django.db import models
from django.contrib.auth.models import User

class Community(models.Model):
    """所有群组的基础模型"""
    COMMUNITY_TYPES = (
        ('course', '课群'),
        ('major', '专业群'),
        ('life', '生活群'),
    )
    
    code = models.CharField(max_length=50, verbose_name="群组代码")
    name = models.CharField(max_length=255, verbose_name="群组名称")
    number = models.CharField(max_length=50, blank=True, verbose_name="群组编号")
    qr_code = models.CharField(max_length=255, default="/placeholder.svg?height=300&width=300", verbose_name="二维码路径")
    type = models.CharField(max_length=20, choices=COMMUNITY_TYPES, verbose_name="群组类型")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.code}: {self.name}"
    
    class Meta:
        verbose_name = "群组"
        verbose_name_plural = "群组"
        ordering = ['type', 'code']

class JoinRequest(models.Model):
    """用户申请加入群组的请求"""
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    )
    
    department_name = models.CharField(max_length=100, verbose_name="院系名称")
    course_number = models.CharField(max_length=50, verbose_name="课程编号")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="处理状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="申请时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="join_requests", verbose_name="申请用户")
    user_email = models.EmailField(blank=True, null=True, verbose_name="用户邮箱")
    
    def __str__(self):
        if self.user:
            return f"{self.department_name} - {self.course_number} (by {self.user.username})"
        return f"{self.department_name} - {self.course_number}"
    
    class Meta:
        verbose_name = "加群申请"
        verbose_name_plural = "加群申请"
        ordering = ['-created_at']
