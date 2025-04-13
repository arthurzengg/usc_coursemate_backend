#!/bin/bash

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# 安装依赖
pip install -r requirements.txt

# 如果.env文件不存在，则从示例文件复制
if [ ! -f .env ]; then
    cp .env.example .env
    echo "已创建.env文件，请编辑该文件填入必要的环境变量。"
fi

# 运行迁移
python manage.py migrate

echo "环境设置完成!"
echo "可以通过 'python manage.py runserver' 启动服务器。" 