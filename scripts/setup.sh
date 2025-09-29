#!/bin/bash

# 91porn智能视频爬虫与推荐系统 - 安装脚本
# 作者: AI Assistant
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    log_success "操作系统: $OS"
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker和Docker Compose已安装"
    
    # 检查内存
    if [[ "$OS" == "linux" ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    else
        MEMORY_GB=$(sysctl -n hw.memsize | awk '{print int($0/1024/1024/1024)}')
    fi
    
    if [ "$MEMORY_GB" -lt 4 ]; then
        log_warning "系统内存不足4GB，可能影响性能"
    else
        log_success "系统内存: ${MEMORY_GB}GB"
    fi
    
    # 检查磁盘空间
    DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_GB" -lt 20 ]; then
        log_warning "磁盘空间不足20GB，可能影响存储"
    else
        log_success "可用磁盘空间: ${DISK_GB}GB"
    fi
}

# 创建目录结构
create_directories() {
    log_info "创建项目目录结构..."
    
    mkdir -p storage/{video_storage,thumbnails,metadata}
    mkdir -p logs
    mkdir -p backups
    mkdir -p config
    
    log_success "目录结构创建完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    # 创建.env文件
    cat > .env << EOF
# 91porn智能视频爬虫与推荐系统环境配置
COMPOSE_PROJECT_NAME=91porn_spider
POSTGRES_DB=mediacms
POSTGRES_USER=mediacms
POSTGRES_PASSWORD=mediacms
REDIS_PASSWORD=
ADMIN_USER=admin
ADMIN_EMAIL=admin@localhost
ADMIN_PASSWORD=admin123
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    
    log_success "环境变量配置完成"
}

# 启动服务
start_services() {
    log_info "启动MediaCMS服务..."
    
    cd mediacms
    
    # 拉取镜像
    log_info "拉取Docker镜像..."
    docker-compose pull
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    if docker-compose ps | grep -q "Up"; then
        log_success "MediaCMS服务启动成功"
    else
        log_error "MediaCMS服务启动失败"
        docker-compose logs
        exit 1
    fi
    
    cd ..
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    # 检查HTTP响应
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200"; then
        log_success "Web服务正常运行"
    else
        log_error "Web服务无法访问"
        exit 1
    fi
    
    # 检查数据库连接
    cd mediacms
    if docker-compose exec -T db pg_isready -U mediacms; then
        log_success "数据库连接正常"
    else
        log_error "数据库连接失败"
        exit 1
    fi
    cd ..
}

# 显示访问信息
show_access_info() {
    log_success "安装完成！"
    echo ""
    echo "=========================================="
    echo "🎉 91porn智能视频爬虫与推荐系统安装成功"
    echo "=========================================="
    echo ""
    echo "📱 访问地址:"
    echo "   主页: http://localhost:80"
    echo "   管理后台: http://localhost:80/admin"
    echo "   API文档: http://localhost:80/api/docs"
    echo ""
    echo "🔑 默认账户:"
    echo "   用户名: admin"
    echo "   密码: admin123"
    echo ""
    echo "📁 项目目录:"
    echo "   配置文件: ./config/"
    echo "   存储目录: ./storage/"
    echo "   日志目录: ./logs/"
    echo ""
    echo "🛠️ 常用命令:"
    echo "   启动服务: cd mediacms && docker-compose up -d"
    echo "   停止服务: cd mediacms && docker-compose down"
    echo "   查看日志: cd mediacms && docker-compose logs -f"
    echo "   重启服务: cd mediacms && docker-compose restart"
    echo ""
    echo "📖 更多信息请查看 README.md"
    echo "=========================================="
}

# 主函数
main() {
    echo "🚀 开始安装91porn智能视频爬虫与推荐系统..."
    echo ""
    
    check_requirements
    create_directories
    setup_environment
    start_services
    verify_installation
    show_access_info
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
