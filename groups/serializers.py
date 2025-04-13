from rest_framework import serializers
from .models import Community, JoinRequest

class CommunitySerializer(serializers.ModelSerializer):
    """群组序列化器，将字段名称与前端保持一致"""
    
    id = serializers.CharField(read_only=True)
    qrCode = serializers.CharField(source='qr_code')
    
    class Meta:
        model = Community
        fields = ['id', 'code', 'name', 'number', 'qrCode', 'type']
        
    def to_representation(self, instance):
        """确保id也作为字符串被输出"""
        ret = super().to_representation(instance)
        # 确保id是字符串格式，与前端期望一致
        ret['id'] = str(instance.id)
        return ret

class JoinRequestSerializer(serializers.ModelSerializer):
    """加群申请序列化器"""
    
    user_id = serializers.IntegerField(source='user.id', required=False, allow_null=True)
    user_email = serializers.EmailField(required=False, allow_null=True)
    
    class Meta:
        model = JoinRequest
        fields = ['id', 'department_name', 'course_number', 'status', 'created_at', 'updated_at', 'user_id', 'user_email']
        read_only_fields = ['status', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        # 处理嵌套数据
        user_data = validated_data.pop('user', None)
        
        # 创建申请
        join_request = JoinRequest.objects.create(**validated_data)
        
        return join_request 