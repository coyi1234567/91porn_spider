#!/bin/bash
# 月榜定时任务脚本

# 设置工作目录
cd "$(dirname "$0")"

# 激活虚拟环境
source venv/bin/activate

# 执行月榜爬取
python3 spider91.py -m

# 记录执行时间
echo "$(date): 月榜爬取完成" >> schedule.log
