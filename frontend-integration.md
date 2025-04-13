# 前端集成指南：Google OAuth登录

本文档提供了如何将前端React应用与Django后端的Google OAuth登录功能集成的详细说明。

## 前端实现步骤

### 1. 更新Google登录处理函数

在`login-page.tsx`中，需要更新`handleGoogleLogin`函数，使其从后端获取登录URL：

```typescript
const handleGoogleLogin = async () => {
  try {
    // 从后端获取Google登录URL
    const response = await fetch('http://localhost:8000/api/auth/google/login/');
    const data = await response.json();
    
    if (!data.login_url) {
      throw new Error('Failed to get login URL');
    }
    
    // 计算弹窗位置，使其在屏幕正中间
    const width = 500;
    const height = 600;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;
    
    // 打开Google登录弹窗，并设置位置参数
    const authWindow = window.open(
      data.login_url,
      'googleLogin',
      `width=${width},height=${height},left=${left},top=${top}`
    );
    
    // 监听来自弹窗的消息
    window.addEventListener('message', (event) => {
      // 验证消息来源和类型
      if (event.data && event.data.type === 'GOOGLE_LOGIN_SUCCESS') {
        const authData = event.data.data;
        
        // 存储认证信息
        localStorage.setItem('access_token', authData.access_token);
        localStorage.setItem('refresh_token', authData.refresh_token);
        localStorage.setItem('user', JSON.stringify(authData.user));
        localStorage.setItem('isLoggedIn', 'true');
        
        // 设置cookie用于服务器端认证检查
        document.cookie = "isLoggedIn=true; path=/; max-age=86400";
        
        // 更新状态并重定向
        setIsLoggedIn(true);
        router.push('/dashboard');
        
        // 关闭弹窗
        if (authWindow) {
          authWindow.close();
        }
      }
    }, false);
  } catch (error) {
    console.error('Google login error:', error);
    alert('Google登录失败，请稍后再试');
  }
};
```

### 2. 创建回调页面

在前端项目中创建一个回调页面，用于接收Google OAuth重定向并将认证信息传递回主应用：

```typescript
// app/oauth2callback/page.tsx
"use client";

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function OAuth2Callback() {
  const searchParams = useSearchParams();
  
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    
    if (error) {
      window.opener.postMessage({ type: 'GOOGLE_LOGIN_ERROR', error }, window.location.origin);
      window.close();
      return;
    }
    
    if (code && state) {
      // 向后端发送授权码
      fetch('http://localhost:8000/api/auth/google/callback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, state }),
      })
      .then(response => response.json())
      .then(data => {
        // 将认证信息传递回主窗口
        window.opener.postMessage({
          type: 'GOOGLE_LOGIN_SUCCESS',
          data
        }, window.location.origin);
        window.close();
      })
      .catch(error => {
        console.error('Error during OAuth callback:', error);
        window.opener.postMessage({
          type: 'GOOGLE_LOGIN_ERROR',
          error: 'Failed to authenticate with the server'
        }, window.location.origin);
        window.close();
      });
    }
  }, [searchParams]);
  
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <h1 className="text-xl font-bold mb-4">正在处理登录...</h1>
        <p>请稍候，不要关闭此窗口。</p>
      </div>
    </div>
  );
}
```

## 后端API端点

后端将提供以下API端点：

1. `GET /api/auth/google/login/` - 生成Google OAuth登录URL
2. `POST /api/auth/google/callback/` - 处理OAuth回调并返回认证信息

## 认证响应格式

成功认证后，后端将返回以下格式的JSON响应：

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "profile_image": "https://lh3.googleusercontent.com/..."
  }
}
```

## 使用认证信息

前端应用应该：

1. 存储`access_token`和`refresh_token`用于后续API请求
2. 在每个需要认证的API请求中添加Authorization头：`Authorization: Bearer {access_token}`
3. 当`access_token`过期时，使用`refresh_token`获取新的令牌

## 注意事项

1. 确保在生产环境中使用HTTPS
2. 正确配置Google OAuth客户端的重定向URI
3. 实现适当的错误处理和用户反馈