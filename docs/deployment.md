# 部署文档

## 概述

本文档详细说明如何部署91porn智能视频爬虫与推荐系统，包括单服务器部署、Docker部署和云服务器部署。

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 50GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB+ SSD
- **网络**: 100Mbps+ 带宽

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

## 快速部署

### 1. 克隆项目

```bash
git clone https://github.com/coyi1234567/91porn_spider.git
cd 91porn_spider
```

### 2. 运行安装脚本

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 3. 访问系统

- 主页: http://localhost:80
- 管理后台: http://localhost:80/admin
- API文档: http://localhost:80/api/docs

## 详细部署步骤

### 环境准备

#### Ubuntu/Debian

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 添加用户到docker组
sudo usermod -aG docker $USER
```

#### CentOS/RHEL

```bash
# 安装Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动Docker
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS

```bash
# 安装Docker Desktop
# 下载并安装: https://www.docker.com/products/docker-desktop

# 或使用Homebrew
brew install --cask docker
```

### 项目配置

#### 1. 创建环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# 数据库配置
POSTGRES_DB=mediacms
POSTGRES_USER=mediacms
POSTGRES_PASSWORD=your_secure_password

# 管理员账户
ADMIN_USER=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_admin_password

# 安全配置
SECRET_KEY=your_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

# Redis配置
REDIS_PASSWORD=your_redis_password
```

#### 2. 配置系统设置

编辑 `config/settings.yaml`：

```yaml
# 爬虫配置
crawler:
  daily_limit: 10
  weekly_limit: 10
  monthly_limit: 10
  crawl_interval: 3600

# 存储配置
storage:
  video_path: "./storage/video_storage"
  max_storage_gb: 100
  cleanup_days: 30

# 推荐系统配置
recommendation:
  model_name: "BAAI/bge-small-zh-v1.5"
  keyword_weight: 0.6
  semantic_weight: 0.4
```

### 启动服务

#### 1. 启动MediaCMS

```bash
cd mediacms
docker-compose up -d
```

#### 2. 检查服务状态

```bash
docker-compose ps
```

应该看到所有服务都在运行：

```
NAME                       STATUS
mediacms-web-1             Up
mediacms-db-1              Up (healthy)
mediacms-redis-1           Up (healthy)
mediacms-celery_worker-1   Up
mediacms-celery_beat-1     Up
```

#### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f db
```

### 初始化系统

#### 1. 创建管理员账户

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 2. 运行数据库迁移

```bash
docker-compose exec web python manage.py migrate
```

#### 3. 收集静态文件

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

#### 4. 创建初始数据

```bash
docker-compose exec web python manage.py loaddata fixtures/initial_data.json
```

## 生产环境部署

### Nginx配置

创建 `/etc/nginx/sites-available/91porn_spider`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 代理到Docker容器
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件缓存
    location /static/ {
        alias /path/to/your/project/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件缓存
    location /media/ {
        alias /path/to/your/project/media/;
        expires 1M;
        add_header Cache-Control "public";
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/91porn_spider /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL证书配置

#### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 防火墙配置

```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 系统服务配置

创建 `/etc/systemd/system/91porn-spider.service`：

```ini
[Unit]
Description=91porn Spider Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/your/project/mediacms
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl enable 91porn-spider.service
sudo systemctl start 91porn-spider.service
```

## 监控和日志

### 系统监控

#### 1. 安装监控工具

```bash
# 安装htop
sudo apt install htop

# 安装iotop
sudo apt install iotop

# 安装nethogs
sudo apt install nethogs
```

#### 2. 配置日志轮转

创建 `/etc/logrotate.d/91porn-spider`：

```
/path/to/your/project/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart web
    endscript
}
```

### 性能监控

#### 1. 监控脚本

创建 `scripts/monitor.sh`：

```bash
#!/bin/bash

# 检查服务状态
check_services() {
    echo "=== 服务状态 ==="
    docker-compose ps
    echo ""
}

# 检查资源使用
check_resources() {
    echo "=== 资源使用 ==="
    echo "CPU使用率:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    echo ""
    
    echo "磁盘使用:"
    df -h
    echo ""
}

# 检查日志错误
check_errors() {
    echo "=== 错误日志 ==="
    docker-compose logs --tail=50 | grep -i error
    echo ""
}

# 主函数
main() {
    check_services
    check_resources
    check_errors
}

main
```

#### 2. 定时监控

```bash
# 添加到crontab
crontab -e

# 每5分钟检查一次
*/5 * * * * /path/to/your/project/scripts/monitor.sh >> /var/log/91porn-monitor.log
```

## 备份和恢复

### 自动备份

#### 1. 配置备份脚本

```bash
chmod +x scripts/backup.sh
```

#### 2. 设置定时备份

```bash
# 添加到crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/your/project/scripts/backup.sh
```

### 手动备份

```bash
# 备份数据库
docker-compose exec db pg_dump -U mediacms mediacms > backup_$(date +%Y%m%d).sql

# 备份配置文件
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/

# 备份媒体文件
tar -czf media_backup_$(date +%Y%m%d).tar.gz storage/
```

### 恢复数据

```bash
# 恢复数据库
docker-compose exec -T db psql -U mediacms mediacms < backup_20250929.sql

# 恢复配置文件
tar -xzf config_backup_20250929.tar.gz

# 恢复媒体文件
tar -xzf media_backup_20250929.tar.gz
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查Docker状态
sudo systemctl status docker

# 检查端口占用
sudo netstat -tlnp | grep :80

# 查看详细日志
docker-compose logs -f
```

#### 2. 数据库连接失败

```bash
# 检查数据库状态
docker-compose exec db pg_isready -U mediacms

# 检查数据库日志
docker-compose logs db

# 重启数据库
docker-compose restart db
```

#### 3. 内存不足

```bash
# 检查内存使用
free -h
docker stats

# 清理Docker缓存
docker system prune -a

# 调整Docker内存限制
# 编辑 docker-compose.yaml
```

#### 4. 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理日志文件
docker-compose logs --tail=0

# 清理未使用的镜像
docker image prune -a
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_media_created_at ON files_media(created_at);
CREATE INDEX idx_media_views ON files_media(views);
CREATE INDEX idx_media_heat ON files_media(heat);

-- 分析表
ANALYZE files_media;
```

#### 2. Redis优化

```bash
# 编辑Redis配置
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. 应用优化

```bash
# 增加工作进程
# 编辑 docker-compose.yaml
environment:
  - UWSGI_PROCESSES=4
  - UWSGI_THREADS=2
```

## 安全配置

### 1. 更新默认密码

```bash
# 修改数据库密码
docker-compose exec db psql -U mediacms -c "ALTER USER mediacms PASSWORD 'new_password';"

# 修改Redis密码
docker-compose exec redis redis-cli CONFIG SET requirepass "new_password"
```

### 2. 配置防火墙

```bash
# 只允许必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. 定期更新

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新Docker镜像
docker-compose pull
docker-compose up -d
```

## 维护指南

### 日常维护

1. **每日检查**
   - 服务状态
   - 磁盘空间
   - 错误日志

2. **每周维护**
   - 清理日志文件
   - 检查备份
   - 更新系统

3. **每月维护**
   - 性能分析
   - 安全更新
   - 容量规划

### 升级指南

1. **备份数据**
2. **停止服务**
3. **更新代码**
4. **运行迁移**
5. **重启服务**
6. **验证功能**

---

如有问题，请查看 [故障排除](#故障排除) 部分或提交 [Issue](https://github.com/coyi1234567/91porn_spider/issues)。
