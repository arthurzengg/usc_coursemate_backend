from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import requests
import json
import os
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer
from .supabase import supabase, supabase_admin
import jwt

# 从环境变量获取Google OAuth配置
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
SUPABASE_URL = os.environ.get('SUPABASE_URL')

# Google OAuth2 URLs
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

class GoogleLoginView(APIView):
    """
    视图用于启动Google OAuth登录流程
    使用Supabase的OAuth提供者或传统方式
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        # 使用Supabase的Google OAuth URL
        use_supabase_auth = True  # 设置为True使用Supabase认证，False使用传统方式
        
        if use_supabase_auth:
            # 在Supabase项目设置中，已配置授权后重定向到前端的callback页面
            # 不需要在URL中添加redirect_to参数，这由Supabase项目配置处理
            auth_url = f"{SUPABASE_URL}/auth/v1/authorize?provider=google"
            
            return Response({'auth_url': auth_url})
        else:
            # 传统Google OAuth URL
            redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
            
            auth_params = {
                'client_id': GOOGLE_CLIENT_ID,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'email profile',
                'access_type': 'offline',
                'prompt': 'consent',
            }
            
            # 构建授权URL
            auth_url = f"{GOOGLE_AUTH_URL}?" + "&".join([f"{key}={value}" for key, value in auth_params.items()])
            
            return Response({'auth_url': auth_url})

class GoogleCallbackView(APIView):
    """
    处理Google OAuth回调
    处理传统方式的OAuth回调或从前端接收Supabase回调代码
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """处理传统OAuth回调"""
        code = request.GET.get('code')
        
        if not code:
            return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 交换授权码获取访问令牌
        redirect_uri = request.build_absolute_uri('/api/auth/google/callback/')
        
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        
        if token_response.status_code != 200:
            return Response({'error': 'Failed to obtain access token'}, status=status.HTTP_400_BAD_REQUEST)
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        
        # 使用访问令牌获取用户信息
        user_info_response = requests.get(
            GOOGLE_USER_INFO_URL,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            return Response({'error': 'Failed to get user info'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_info = user_info_response.json()
        
        # 从Google用户信息中提取相关数据
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        # 查找或创建用户
        try:
            # 尝试通过Google ID查找用户资料
            profile = UserProfile.objects.get(google_id=google_id)
            user = profile.user
            # 更新用户信息
            user.first_name = name.split()[0] if name else ''
            user.last_name = ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
            user.email = email
            user.save()
            # 更新用户资料
            profile.profile_image = picture
            profile.save()
        except UserProfile.DoesNotExist:
            # 创建新用户和资料
            username = email.split('@')[0]
            # 确保用户名唯一
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            user = User.objects.create(
                username=username,
                email=email,
                first_name=name.split()[0] if name else '',
                last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else ''
            )
            
            # 创建用户资料
            UserProfile.objects.create(
                user=user,
                google_id=google_id,
                profile_image=picture
            )
        
        # 序列化用户数据
        serializer = UserSerializer(user)
        
        # 重定向到前端，带上用户数据
        redirect_to = f"{FRONTEND_URL}/oauth2callback?user={json.dumps(serializer.data)}"
        return redirect(redirect_to)
    
    def post(self, request):
        """处理Supabase OAuth回调"""
        code = request.data.get('code')
        
        if not code:
            return Response({'error': '授权码未提供'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 使用Supabase Admin客户端交换授权码获取会话
            auth_response = supabase_admin.auth.admin.exchange_code_for_session({"code": code})
            
            # 获取Supabase用户数据
            user_data = auth_response.user
            
            if not user_data:
                return Response({'error': '无法获取用户数据'}, status=status.HTTP_400_BAD_REQUEST)
                
            # 提取关键用户信息
            email = user_data.get('email')
            identities = user_data.get('identities', [])
            
            if not identities:
                return Response({'error': '用户身份信息缺失'}, status=status.HTTP_400_BAD_REQUEST)
                
            provider_id = identities[0].get('provider_id')  # Google ID
            identity_data = identities[0].get('identity_data', {})
            
            full_name = identity_data.get('full_name', '')
            avatar_url = identity_data.get('avatar_url', '')
            
            # 从全名中分割姓和名
            name_parts = full_name.split() if full_name else ['', '']
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            # 在Django中同步用户数据
            # 查找或创建用户
            try:
                # 尝试通过Google ID查找用户资料
                profile = UserProfile.objects.get(google_id=provider_id)
                user = profile.user
                # 更新用户信息
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                # 更新用户资料
                profile.profile_image = avatar_url
                profile.save()
            except UserProfile.DoesNotExist:
                # 创建新用户和资料
                username = email.split('@')[0]
                # 确保用户名唯一
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                    
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # 创建用户资料
                UserProfile.objects.create(
                    user=user,
                    google_id=provider_id,
                    profile_image=avatar_url
                )
            
            # 序列化用户数据
            serializer = UserSerializer(user)
            
            # 返回用户数据和Supabase会话
            return Response({
                'user': serializer.data,
                'session': auth_response.session,
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SyncUserView(APIView):
    """
    同步Supabase用户数据到Django后端
    """
    permission_classes = [AllowAny]  # 或使用适当的权限类
    
    def post(self, request):
        try:
            # 获取并验证Supabase JWT令牌
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                # 如果没有Authorization头，尝试从请求数据中获取令牌
                data = request.data
                supabase_id = data.get('supabase_id')
                email = data.get('email')
                
                # 如果至少有这些基本信息，允许请求通过（开发环境）
                if supabase_id and email:
                    # 从请求体获取用户数据
                    first_name = data.get('first_name', '')
                    last_name = data.get('last_name', '')
                    profile_image = data.get('profile_image')
                    
                    # 直接处理用户数据，跳过令牌验证（仅用于开发/测试）
                    return self._process_user_data(supabase_id, email, first_name, last_name, profile_image)
                else:
                    return Response({'error': '未提供有效的认证令牌或用户数据不完整'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 如果有Authorization头，进行正常的令牌验证流程
            token = auth_header.split(' ')[1]
            
            try:
                # 解码JWT但不验证签名（用于开发测试）
                # 打印令牌内容以便调试
                print("JWT令牌:", token[:20] + "..." if len(token) > 20 else token)
                
                payload = jwt.decode(token, options={"verify_signature": False})
                print("JWT payload:", payload)
                
                supabase_user_id = payload.get('sub')
                
                if not supabase_user_id:
                    return Response({'error': '无效的用户令牌'}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                print("JWT解码错误:", str(e))
                # 尝试更宽松的处理方式 - 直接从请求数据中获取用户ID
                data = request.data
                supabase_id = data.get('supabase_id')
                if not supabase_id:
                    return Response({'error': f'令牌解析失败: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)
                supabase_user_id = supabase_id
            
            # 从请求体获取用户数据
            data = request.data
            email = data.get('email')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')
            profile_image = data.get('profile_image')
            
            if not email:
                return Response({'error': '缺少必要的用户信息'}, status=status.HTTP_400_BAD_REQUEST)
            
            return self._process_user_data(supabase_user_id, email, first_name, last_name, profile_image)
            
        except Exception as e:
            print("处理请求时出错:", str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _process_user_data(self, supabase_id, email, first_name, last_name, profile_image):
        """处理用户数据的辅助方法"""
        try:
            # 尝试通过Supabase ID查找用户资料
            profile = UserProfile.objects.get(google_id=supabase_id)
            user = profile.user
            # 更新用户信息
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            # 更新用户资料
            profile.profile_image = profile_image
            profile.save()
        except UserProfile.DoesNotExist:
            # 创建新用户和资料
            username = email.split('@')[0]
            # 确保用户名唯一
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
                
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # 创建用户资料
            UserProfile.objects.create(
                user=user,
                google_id=supabase_id,
                profile_image=profile_image
            )
        
        # 序列化用户数据
        serializer = UserSerializer(user)
        
        return Response(serializer.data)