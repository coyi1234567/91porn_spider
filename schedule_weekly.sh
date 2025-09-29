#!/bin/bash
# 周榜定时任务脚本

# 设置工作目录
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 执行周榜爬取
python3 spider91.py -w

# 记录执行时间
echo "$(date): 周榜爬取完成" >> schedule.log
