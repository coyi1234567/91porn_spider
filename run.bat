@echo off
echo === 91porn_spider Python版本 ===
echo 正在启动爬虫...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
echo 检查依赖...
pip install -r requirements.txt > nul 2>&1

REM 检查Chrome浏览器
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    echo 警告: 未检测到Chrome浏览器，请确保已安装Chrome
)

REM 运行爬虫
echo 启动爬虫程序...
python spider91.py %*
