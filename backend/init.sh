#!/bin/bash
# 数据库初始化脚本

set -e

echo "========================================"
echo "🎵 极简广播剧系统 - 数据库初始化"
echo "========================================"

# 检查是否在正确的目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 请在 backend 目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 正在安装依赖..."
pip install -q -r requirements.txt

# 创建数据目录
mkdir -p data

# 初始化数据库
echo "🔧 正在初始化数据库..."
python -m app.db.init_db

echo ""
echo "========================================"
echo "✅ 初始化完成！"
echo "========================================"
echo ""
echo "启动服务："
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API 文档："
echo "  http://localhost:8000/docs"
echo ""
