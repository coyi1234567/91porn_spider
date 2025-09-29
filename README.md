# 91porn视频爬虫 - Python版本

基于原始Go项目重写的Python版本，支持日榜、周榜、月榜视频爬取，具备完整的去重机制和元数据管理功能。

## 功能特性

- 🎯 **多榜单支持**: 日榜、周榜、月榜前10名视频
- 📁 **智能存储**: 按日期和类型分文件夹存储
- 🏷️ **丰富命名**: 文件名包含排名、分数、热度、收藏数量
- 🔄 **去重机制**: 基于viewkey和文件hash双重去重
- 📊 **元数据管理**: 完整的视频信息记录和JSON导出
- 🚀 **高效下载**: 支持断点续传和错误重试
- 🔧 **配置灵活**: 支持代理配置和评分规则自定义

## 安装要求

- Python 3.8+
- Chrome浏览器
- 网络连接

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/coyi1234567/91porn_spider.git
cd 91porn_spider
```

### 2. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动Chrome远程调试
```bash
# 启动Chrome并开启远程调试端口
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug
```

### 4. 运行爬虫
```bash
# 日榜爬取（前10个视频）
python3 spider91.py -d

# 周榜爬取（前10个视频）
python3 spider91.py -w

# 月榜爬取（前10个视频）
python3 spider91.py -m

# 自定义页面爬取
python3 spider91.py -c -u "https://91porn.com/index.php"
```

## 存储结构

```
videos_storage/
├── daily/                    # 日榜视频
│   └── 20250929/            # 按日期分文件夹
│       ├── [DAILY_20250929]_RANK01_SCORE000_HEAT000005_FAV2000_视频标题_viewkey.mp4
│       └── ...
├── weekly/                   # 周榜视频
│   └── 20240923/            # 周一日期
├── monthly/                  # 月榜视频
│   └── 202409/              # 按年月分文件夹
├── custom/                   # 自定义爬取
└── metadata/                 # 元数据
    ├── videos.db            # SQLite数据库
    └── daily_20250929.json  # 榜单元数据
```

## 文件命名规则

格式: `[类型_日期]_RANK排名_SCORE分数_HEAT热度_FAV收藏_标题_viewkey.mp4`

示例: `[DAILY_20250929]_RANK01_SCORE000_HEAT000005_FAV2000_酒吧带走的极品女神_7973c5611b4b35bd2726.mp4`

## 配置说明

### 代理配置 (proxyConfig.yaml)
```yaml
proxy_url: "http://proxy.example.com:8080"
```

### 关键词评分 (score/wordValue.txt)
```
关键词=分数
爆乳=10
3p=8
少妇=5
```

### 作者评分 (score/ownValue.txt)
```
作者名=分数
作者A=10
作者B=8
```

## 命令行参数

```bash
python3 spider91.py [选项]

选项:
  -d, --daily      日榜爬取模式 (前10个)
  -w, --weekly     周榜爬取模式 (前10个)
  -m, --monthly    月榜爬取模式 (前10个)
  -c, --crawl      爬取指定页面
  -u, --url URL    要爬取的页面URL
  -s, --save-path  视频保存路径 (默认: ./videos_storage)
```

## 功能详解

### 1. 视频信息提取
- 标题、作者、时长、观看次数
- 热度、收藏数量、评论数量
- 点赞数、踩数、评分

### 2. 去重机制
- **ViewKey去重**: 基于视频唯一标识
- **文件Hash去重**: 基于MD5值避免重复下载
- **数据库记录**: 完整的下载历史记录

### 3. 评分系统
- 关键词匹配评分
- 作者权重评分
- 观看次数加权
- 综合排名计算

### 4. 元数据管理
- SQLite数据库存储
- JSON格式导出
- 完整的视频信息记录

## 定时任务

### Linux/Mac (crontab)
```bash
# 每日8点执行日榜爬取
0 8 * * * cd /path/to/91porn_spider && source venv/bin/activate && python3 spider91.py -d

# 每周六9点执行周榜爬取
0 9 * * 6 cd /path/to/91porn_spider && source venv/bin/activate && python3 spider91.py -w

# 每月1号10点执行月榜爬取
0 10 1 * * cd /path/to/91porn_spider && source venv/bin/activate && python3 spider91.py -m
```

### Windows (任务计划程序)
创建定时任务，执行以下命令：
```cmd
cd C:\path\to\91porn_spider
venv\Scripts\activate
python spider91.py -d
```

## 故障排除

### 1. Chrome连接失败
```bash
# 确保Chrome已启动远程调试
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug
```

### 2. 网络连接问题
- 检查网络连接
- 配置代理设置
- 检查防火墙设置

### 3. 年龄验证页面
- 确保Chrome已登录91porn账户
- 手动处理年龄验证后运行爬虫

### 4. 下载失败
- 检查磁盘空间
- 检查文件权限
- 查看日志文件

## 日志文件

- `spider91.log`: 详细的运行日志
- 包含错误信息、下载进度、解析结果

## 注意事项

1. **合法使用**: 请遵守相关法律法规，仅用于学习研究
2. **网络礼仪**: 避免频繁请求，设置合理的延迟
3. **存储管理**: 定期清理旧文件，注意磁盘空间
4. **隐私保护**: 妥善保管下载的视频文件

## 技术栈

- **Python 3.8+**: 主要编程语言
- **Selenium**: 网页自动化
- **SQLite**: 数据存储
- **Chrome**: 浏览器引擎
- **curl**: 视频下载

## 更新日志

### v1.0.0 (2025-09-29)
- ✅ 完整的Python重写
- ✅ 日榜、周榜、月榜支持
- ✅ 智能文件命名和存储
- ✅ 去重机制和元数据管理
- ✅ 热度和收藏数量提取
- ✅ 完整的错误处理和日志

## 许可证

本项目基于原始Go项目重写，遵循相同的开源许可证。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题，请通过GitHub Issues联系。