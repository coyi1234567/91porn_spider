#!/bin/bash

# 91porn智能视频爬虫与推荐系统 - 备份脚本
# 作者: AI Assistant
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="91porn_spider_backup_${DATE}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

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

# 创建备份目录
create_backup_dir() {
    log_info "创建备份目录..."
    mkdir -p "$BACKUP_PATH"
    log_success "备份目录创建完成: $BACKUP_PATH"
}

# 备份数据库
backup_database() {
    log_info "备份PostgreSQL数据库..."
    
    cd mediacms
    
    # 备份数据库
    docker-compose exec -T db pg_dump -U mediacms mediacms > "../${BACKUP_PATH}/database.sql"
    
    if [ $? -eq 0 ]; then
        log_success "数据库备份完成"
    else
        log_error "数据库备份失败"
        exit 1
    fi
    
    cd ..
}

# 备份配置文件
backup_config() {
    log_info "备份配置文件..."
    
    # 备份系统配置
    cp -r config/ "${BACKUP_PATH}/config/"
    
    # 备份环境变量
    if [ -f .env ]; then
        cp .env "${BACKUP_PATH}/"
    fi
    
    # 备份Docker配置
    cp mediacms/docker-compose.yaml "${BACKUP_PATH}/"
    
    log_success "配置文件备份完成"
}

# 备份元数据
backup_metadata() {
    log_info "备份元数据..."
    
    # 备份存储元数据
    if [ -d storage/metadata ]; then
        cp -r storage/metadata/ "${BACKUP_PATH}/metadata/"
    fi
    
    # 备份日志
    if [ -d logs ]; then
        cp -r logs/ "${BACKUP_PATH}/logs/"
    fi
    
    log_success "元数据备份完成"
}

# 备份向量数据库
backup_vector_db() {
    log_info "备份向量数据库..."
    
    # 检查Chroma是否运行
    if docker ps | grep -q chroma; then
        # 备份Chroma数据
        docker exec chroma tar -czf /tmp/chroma_backup.tar.gz /chroma/chroma
        docker cp chroma:/tmp/chroma_backup.tar.gz "${BACKUP_PATH}/chroma_backup.tar.gz"
        log_success "向量数据库备份完成"
    else
        log_warning "Chroma服务未运行，跳过向量数据库备份"
    fi
}

# 创建备份信息文件
create_backup_info() {
    log_info "创建备份信息文件..."
    
    cat > "${BACKUP_PATH}/backup_info.txt" << EOF
# 91porn智能视频爬虫与推荐系统备份信息

备份时间: $(date)
备份版本: 1.0.0
系统信息: $(uname -a)
Docker版本: $(docker --version)
Docker Compose版本: $(docker-compose --version)

备份内容:
- 数据库: database.sql
- 配置文件: config/
- 元数据: metadata/
- 日志文件: logs/
- 向量数据库: chroma_backup.tar.gz (如果可用)

恢复说明:
1. 停止所有服务: cd mediacms && docker-compose down
2. 恢复数据库: docker-compose exec -T db psql -U mediacms mediacms < database.sql
3. 恢复配置文件: cp -r config/ ../../config/
4. 恢复元数据: cp -r metadata/ ../../storage/metadata/
5. 启动服务: docker-compose up -d

注意事项:
- 请确保在恢复前备份当前数据
- 恢复后需要重新启动所有服务
- 检查配置文件是否正确
EOF
    
    log_success "备份信息文件创建完成"
}

# 压缩备份
compress_backup() {
    log_info "压缩备份文件..."
    
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    
    if [ $? -eq 0 ]; then
        log_success "备份压缩完成: ${BACKUP_NAME}.tar.gz"
        # 删除未压缩的目录
        rm -rf "$BACKUP_NAME"
    else
        log_error "备份压缩失败"
        exit 1
    fi
    
    cd ..
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份文件..."
    
    # 保留最近7天的备份
    find "$BACKUP_DIR" -name "91porn_spider_backup_*.tar.gz" -mtime +7 -delete
    
    log_success "旧备份清理完成"
}

# 显示备份信息
show_backup_info() {
    log_success "备份完成！"
    echo ""
    echo "=========================================="
    echo "📦 备份信息"
    echo "=========================================="
    echo "备份文件: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "备份大小: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
    echo "备份时间: $(date)"
    echo ""
    echo "🔄 恢复命令:"
    echo "   tar -xzf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "   cd ${BACKUP_NAME}"
    echo "   # 按照 backup_info.txt 中的说明进行恢复"
    echo ""
    echo "📁 备份目录: $BACKUP_DIR"
    echo "=========================================="
}

# 主函数
main() {
    echo "🔄 开始备份91porn智能视频爬虫与推荐系统..."
    echo ""
    
    create_backup_dir
    backup_database
    backup_config
    backup_metadata
    backup_vector_db
    create_backup_info
    compress_backup
    cleanup_old_backups
    show_backup_info
}

# 错误处理
trap 'log_error "备份过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
