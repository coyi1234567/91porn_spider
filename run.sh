#!/bin/bash

# 91porn_spider 启动脚本

echo "=== 91porn_spider Python版本 ==="
echo "正在启动爬虫..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 检查Chrome浏览器
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null; then
    echo "警告: 未检测到Chrome浏览器，请确保已安装Chrome"
fi

# 运行爬虫
echo "启动爬虫程序..."
python3 spider91.py "$@"
