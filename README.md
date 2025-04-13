# USCCoursemate 后端

这是USCCoursemate项目的Django后端，提供API服务和Google OAuth登录功能。

## 项目结构

```
backend/
  ├── usccoursemate/        # Django项目主目录
  │   ├── __init__.py
  │   ├── settings.py       # 项目设置
  │   ├── urls.py           # URL路由配置
  │   ├── asgi.py           # ASGI配置
  │   └── wsgi.py           # WSGI配置
  ├── authentication/       # 认证应用
  │   ├── __init__.py
  │   ├── admin.py
  │   ├── apps.py
  │   ├── models.py         # 用户模型
  │   ├── serializers.py    # 序列化器
  │   ├── urls.py           # 认证URL路由
  │   └── views.py          # 视图函数
  ├── manage.py             # Django管理脚本
  ├── requirements.txt      # 项目依赖
  └── .env.example          # 环境变量示例
```

## 本地开发

### 环境设置

1. 克隆仓库并进入项目目录
```bash
git clone https://github.com/yourusername/USCCoursemate.git
cd USCCoursemate/backend
```

2. 创建虚拟环境并激活
```bash
python -m venv venv
source venv/bin/activate  # 在Windows上使用: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 复制环境变量示例文件并填写必要信息
```bash
cp .env.example .env
# 编辑.env文件添加必要的密钥和配置
```

5. 运行数据库迁移
```bash
python manage.py migrate
```

6. 启动开发服务器
```bash
python manage.py runserver
```

## 部署到Render

1. 将代码推送到GitHub仓库

2. 在Render.com创建一个新的Web Service
   - 连接到你的GitHub仓库
   - 选择"Python"作为运行时环境
   - 设置构建命令为`./build.sh`
   - 设置启动命令为`gunicorn usccoursemate.wsgi:application`

3. 环境变量配置
   在Render的环境变量设置中添加以下变量:
   - SECRET_KEY (使用随机生成的安全密钥)
   - DEBUG (设置为False)
   - ALLOWED_HOSTS (包含你的Render域名)
   - FRONTEND_URL (指向你的前端应用URL)
   - GOOGLE_CLIENT_ID
   - GOOGLE_CLIENT_SECRET
   - SUPABASE_URL
   - SUPABASE_KEY
   - SUPABASE_SECRET
   - DATABASE_URL

4. 提交并推送代码后，Render将自动构建并部署你的应用

## Google OAuth设置

1. 访问[Google Cloud Console](https://console.cloud.google.com/)
2. 创建一个新项目或选择现有项目
3. 导航到「API和服务」>「凭据」
4. 点击「创建凭据」>「OAuth客户端ID」
5. 设置应用类型为「Web应用」
6. 添加授权重定向URI: `http://localhost:3000/oauth2callback`（开发环境）
7. 创建后，记下客户端ID和客户端密钥
8. 将这些值添加到`.env`文件中

## API端点

### 认证

- `GET /api/auth/google/login/` - 获取Google OAuth登录URL
- `POST /api/auth/google/callback/` - 处理OAuth回调并返回认证信息

## 环境变量

- `SECRET_KEY` - Django密钥
- `DEBUG` - 调试模式（True/False）
- `ALLOWED_HOSTS` - 允许的主机列表
- `GOOGLE_CLIENT_ID` - Google OAuth客户端ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth客户端密钥
- `FRONTEND_URL` - 前端应用URL（用于CORS和重定向）
- `SUPABASE_URL` - Supabase URL
- `SUPABASE_KEY` - Supabase API密钥
- `SUPABASE_SECRET` - Supabase密钥
- `DATABASE_URL` - 数据库连接URL