from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Community, JoinRequest
from .serializers import CommunitySerializer, JoinRequestSerializer

# Create your views here.

class CommunityViewSet(viewsets.ModelViewSet):
    """
    群组视图集，处理所有群组的CRUD操作
    """
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """允许按类型过滤群组"""
        queryset = Community.objects.all()
        community_type = self.request.query_params.get('type')
        if community_type:
            queryset = queryset.filter(type=community_type)
        return queryset

class JoinRequestViewSet(viewsets.ModelViewSet):
    """
    加群申请视图集，处理所有加群申请的CRUD操作
    """
    queryset = JoinRequest.objects.all()
    serializer_class = JoinRequestSerializer
    
    def get_permissions(self):
        """
        创建申请时允许匿名访问，其他操作需要认证
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        创建申请，同时关联用户信息
        """
        data = request.data.copy()
        
        # 检查是否有用户信息
        user_id = data.get('user_id')
        user_email = data.get('user_email')
        
        # 创建申请
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # 保存申请，关联用户
        join_request = serializer.save()
        
        # 如果有用户ID，尝试关联用户
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                join_request.user = user
                join_request.save()
            except User.DoesNotExist:
                pass
        
        # 保存用户邮箱
        if user_email and not join_request.user_email:
            join_request.user_email = user_email
            join_request.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """默认只返回未处理的申请"""
        queryset = JoinRequest.objects.all()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
