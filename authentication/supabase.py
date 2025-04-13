from supabase import create_client
import os

# 从环境变量获取Supabase配置
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase_secret = os.environ.get("SUPABASE_SECRET")  # 服务角色密钥，用于管理员操作

# 创建Supabase客户端
supabase = create_client(supabase_url, supabase_key)

# 创建服务角色客户端（具有管理权限）
supabase_admin = create_client(supabase_url, supabase_secret) 