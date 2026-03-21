#!/bin/bash
# 启动音频剧后端服务（端口8001）

cd "$(dirname "$0")/backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
