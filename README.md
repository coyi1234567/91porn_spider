# 91porn_spider

#### 介绍
91视频网站爬虫工具，可以批量或单独爬取视频。现已完全重写为Python版本，功能更强大，使用更简单。
不带参数运行程序时，进入日常爬取模式，固定每天8点爬取24小时内发布的30个评分最高的视频，评分由关键字、视频时长、作者分三项评分组成(score下的两个txt定义了关键词评分和作者评分，分数范围[-∞，100])。每周六9点会爬取本周评分最高的30个最热视频并把当周的视频整理到一个文件夹下。程序有去重机制不会重复下载同一个视频。

#### 软件架构
基于Python 3.8+编写，使用Selenium + Chrome浏览器进行网页抓取，支持代理、去重、定时任务等功能。

#### 安装教程

**方法一：使用启动脚本（推荐）**
```bash
# Linux/Mac
./run.sh

# Windows
run.bat
```

**方法二：手动安装**
1. 安装Chrome浏览器
2. 安装Python 3.8+
3. 创建虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate.bat  # Windows
   ```
4. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```


#### 使用说明

1. 参数说明  
   -c 爬取页面  
   -u 爬取的网页 可以是单个视频的页面也可以使是类似首页的多个视频的页面。  
   -o 视频存储路径  
   -p 代理地址  
   -t 同时爬取的视频个数  
   -now 爬取前X天的的视频
   -n 与-now一起使用，表示存评分前X个视频

2. 示例  
   **单个视频爬取**  
   ```bash
   python3 spider91.py -c -u "http://91porn.com/view_video.php?viewkey=8cd0148b3fe08d4a4c2f" -p "http://127.0.0.1:10808"
   ```
   
   **单页多个视频爬取**  
   ```bash
   python3 spider91.py -c -u "http://91porn.com/v.php?category=rf&viewtype=basic&page=2" -p "http://127.0.0.1:10808"
   ```
   
   **爬取前3天评分前100的视频**  
   ```bash
   python3 spider91.py -now 3 -n 100
   ```
   
   **定时任务模式（默认）**  
   ```bash
   python3 spider91.py
   ```

3. 新增docker版本  
   https://hub.docker.com/repository/docker/templelv/spider91

   ```
   docker run --restart=always -it --name spider91 \
   -v /dir_to_save/:/root/spider91/save \
   templelv/spider91 sh -c 'service supervisor start && /bin/bash' 
   ```
   /dir_to_save为用户设置的视频保存路径  
   docker attach spider91 命令可以进入容器终端  
   容器终端中执行/root/spider91/update.sh   将更新代码为github上最新并编译重新执行。  
   代理列表通过修改配置文件更新，配置文件路径/root/spider91/proxyConfig.yaml  
   推荐使用passwall建立多个代理。

#### Vercel部署

本项目已配置支持Vercel部署（Python版本）：

**为什么选择Python而不是Go？**
- ✅ Vercel对Python支持更成熟稳定
- ✅ 配置更简单，无需复杂的运行时版本
- ✅ 依赖管理更灵活
- ✅ 调试和错误处理更容易

**部署步骤：**
1. 将代码推送到GitHub仓库
2. 在Vercel中导入GitHub仓库
3. 自动部署完成

**API端点：**
- `/` - 返回API状态信息
- `/api` - 返回API状态信息

**API响应示例：**
```json
{
  "message": "91porn_spider API is running successfully!",
  "status": "success",
  "framework": "Python"
}
```

注意：由于Vercel的无服务器环境限制，完整的爬虫功能需要在本地环境或支持Chrome的服务器环境中运行。  
