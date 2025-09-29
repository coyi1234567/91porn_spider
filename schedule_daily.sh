#!/bin/bash
# 日榜定时任务脚本

# 设置工作目录
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 执行日榜爬取
python3 spider91.py -d

# 记录执行时间
echo "$(date): 日榜爬取完成" >> schedule.log
