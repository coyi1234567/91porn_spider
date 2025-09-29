# API 文档

## 概述

91porn智能视频爬虫与推荐系统提供完整的RESTful API，基于MediaCMS的Django REST Framework构建。

## 基础信息

- **Base URL**: `http://localhost:80/api/`
- **认证方式**: Token认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 获取Token

```http
POST /api/auth/token/
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

**响应**:
```json
{
    "token": "your_access_token_here",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@localhost"
    }
}
```

### 使用Token

在请求头中添加认证信息：

```http
Authorization: Token your_access_token_here
```

## 媒体管理 API

### 获取媒体列表

```http
GET /api/media/
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20)
- `search`: 搜索关键词
- `category`: 分类ID
- `ordering`: 排序字段 (如: `-created_at`, `title`)

**响应**:
```json
{
    "count": 100,
    "next": "http://localhost:80/api/media/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "视频标题",
            "description": "视频描述",
            "friendly_token": "abc123",
            "media_file": "http://localhost:80/media/videos/video.mp4",
            "thumbnail": "http://localhost:80/media/thumbnails/thumb.jpg",
            "duration": 300,
            "views": 1000,
            "likes": 50,
            "dislikes": 5,
            "created_at": "2025-09-29T10:00:00Z",
            "user": {
                "id": 1,
                "username": "admin"
            },
            "category": {
                "id": 1,
                "name": "分类名称"
            },
            "tags": ["标签1", "标签2"],
            "heat": 95.5,
            "favorites": 25,
            "score": 4.8,
            "rank_type": "daily",
            "rank_date": "2025-09-29",
            "rank_position": 1
        }
    ]
}
```

### 获取单个媒体

```http
GET /api/media/{friendly_token}/
```

**响应**:
```json
{
    "id": 1,
    "title": "视频标题",
    "description": "视频描述",
    "friendly_token": "abc123",
    "media_file": "http://localhost:80/media/videos/video.mp4",
    "thumbnail": "http://localhost:80/media/thumbnails/thumb.jpg",
    "duration": 300,
    "views": 1000,
    "likes": 50,
    "dislikes": 5,
    "created_at": "2025-09-29T10:00:00Z",
    "user": {
        "id": 1,
        "username": "admin"
    },
    "category": {
        "id": 1,
        "name": "分类名称"
    },
    "tags": ["标签1", "标签2"],
    "heat": 95.5,
    "favorites": 25,
    "score": 4.8,
    "rank_type": "daily",
    "rank_date": "2025-09-29",
    "rank_position": 1,
    "metadata": {
        "author": "作者名称",
        "publish_date": "2025-09-29",
        "collection_volume": 100,
        "viewkey": "abc123def456"
    }
}
```

## 排行榜 API

### 获取日榜

```http
GET /api/rankings/daily/
```

**查询参数**:
- `date`: 日期 (格式: YYYY-MM-DD, 默认: 今天)
- `limit`: 数量限制 (默认: 10)

**响应**:
```json
{
    "date": "2025-09-29",
    "type": "daily",
    "videos": [
        {
            "id": 1,
            "title": "视频标题",
            "friendly_token": "abc123",
            "thumbnail": "http://localhost:80/media/thumbnails/thumb.jpg",
            "duration": 300,
            "views": 1000,
            "heat": 95.5,
            "favorites": 25,
            "score": 4.8,
            "rank_position": 1
        }
    ]
}
```

### 获取周榜

```http
GET /api/rankings/weekly/
```

### 获取月榜

```http
GET /api/rankings/monthly/
```

## 推荐系统 API

### 获取推荐视频

```http
GET /api/recommendations/
```

**查询参数**:
- `user_id`: 用户ID (可选)
- `limit`: 推荐数量 (默认: 20)
- `type`: 推荐类型 (`keyword`, `semantic`, `hybrid`)

**响应**:
```json
{
    "type": "hybrid",
    "user_id": 1,
    "videos": [
        {
            "id": 1,
            "title": "推荐视频标题",
            "friendly_token": "abc123",
            "thumbnail": "http://localhost:80/media/thumbnails/thumb.jpg",
            "duration": 300,
            "views": 1000,
            "heat": 95.5,
            "favorites": 25,
            "score": 4.8,
            "similarity_score": 0.95,
            "recommendation_reason": "基于您的观看历史和相似视频"
        }
    ]
}
```

### 基于视频推荐

```http
GET /api/recommendations/similar/{friendly_token}/
```

**查询参数**:
- `limit`: 推荐数量 (默认: 10)
- `type`: 推荐类型 (`keyword`, `semantic`, `hybrid`)

## 搜索 API

### 关键词搜索

```http
GET /api/search/
```

**查询参数**:
- `q`: 搜索关键词
- `type`: 搜索类型 (`keyword`, `semantic`, `hybrid`)
- `limit`: 结果数量 (默认: 20)
- `page`: 页码 (默认: 1)

**响应**:
```json
{
    "query": "搜索关键词",
    "type": "hybrid",
    "count": 50,
    "next": "http://localhost:80/api/search/?q=关键词&page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "搜索结果标题",
            "friendly_token": "abc123",
            "thumbnail": "http://localhost:80/media/thumbnails/thumb.jpg",
            "duration": 300,
            "views": 1000,
            "heat": 95.5,
            "favorites": 25,
            "score": 4.8,
            "relevance_score": 0.95,
            "match_type": "title"
        }
    ]
}
```

## 爬虫管理 API

### 获取爬虫状态

```http
GET /api/crawler/status/
```

**响应**:
```json
{
    "status": "running",
    "last_crawl": "2025-09-29T10:00:00Z",
    "next_crawl": "2025-09-29T11:00:00Z",
    "daily_count": 10,
    "weekly_count": 10,
    "monthly_count": 10,
    "total_videos": 1000,
    "errors": []
}
```

### 手动触发爬取

```http
POST /api/crawler/crawl/
Content-Type: application/json

{
    "type": "daily",
    "limit": 10
}
```

**响应**:
```json
{
    "status": "started",
    "task_id": "task_123",
    "message": "爬取任务已启动"
}
```

### 获取爬取任务状态

```http
GET /api/crawler/tasks/{task_id}/
```

**响应**:
```json
{
    "task_id": "task_123",
    "status": "completed",
    "progress": 100,
    "result": {
        "videos_crawled": 10,
        "videos_saved": 8,
        "errors": []
    },
    "created_at": "2025-09-29T10:00:00Z",
    "completed_at": "2025-09-29T10:05:00Z"
}
```

## 系统配置 API

### 获取系统配置

```http
GET /api/config/
```

**响应**:
```json
{
    "crawler": {
        "daily_limit": 10,
        "weekly_limit": 10,
        "monthly_limit": 10,
        "crawl_interval": 3600
    },
    "storage": {
        "max_storage_gb": 100,
        "cleanup_days": 30,
        "compression": true
    },
    "recommendation": {
        "keyword_weight": 0.6,
        "semantic_weight": 0.4,
        "popularity_weight": 0.2
    }
}
```

### 更新系统配置

```http
PUT /api/config/
Content-Type: application/json
Authorization: Token your_access_token_here

{
    "crawler": {
        "daily_limit": 15,
        "weekly_limit": 15,
        "monthly_limit": 15
    }
}
```

## 用户管理 API

### 获取用户信息

```http
GET /api/users/profile/
Authorization: Token your_access_token_here
```

**响应**:
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@localhost",
    "first_name": "",
    "last_name": "",
    "date_joined": "2025-09-29T10:00:00Z",
    "is_staff": true,
    "is_superuser": true,
    "preferences": {
        "theme": "dark",
        "language": "zh-CN",
        "notifications": true
    }
}
```

### 更新用户偏好

```http
PUT /api/users/preferences/
Content-Type: application/json
Authorization: Token your_access_token_here

{
    "theme": "light",
    "language": "en-US",
    "notifications": false
}
```

## 错误处理

### 错误响应格式

```json
{
    "error": "错误类型",
    "message": "错误描述",
    "details": {
        "field": "具体错误信息"
    },
    "code": 400
}
```

### 常见错误码

- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 速率限制

- **认证用户**: 1000 请求/小时
- **匿名用户**: 100 请求/小时
- **爬虫API**: 10 请求/小时

## 示例代码

### Python

```python
import requests

# 获取Token
response = requests.post('http://localhost:80/api/auth/token/', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']

# 设置认证头
headers = {'Authorization': f'Token {token}'}

# 获取媒体列表
response = requests.get('http://localhost:80/api/media/', headers=headers)
videos = response.json()['results']

# 搜索视频
response = requests.get('http://localhost:80/api/search/', 
                       params={'q': '关键词'}, headers=headers)
results = response.json()['results']
```

### JavaScript

```javascript
// 获取Token
const tokenResponse = await fetch('http://localhost:80/api/auth/token/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
    })
});
const {token} = await tokenResponse.json();

// 设置认证头
const headers = {'Authorization': `Token ${token}`};

// 获取媒体列表
const mediaResponse = await fetch('http://localhost:80/api/media/', {headers});
const {results: videos} = await mediaResponse.json();

// 搜索视频
const searchResponse = await fetch('http://localhost:80/api/search/?q=关键词', {headers});
const {results} = await searchResponse.json();
```

## 更新日志

### v1.0.0 (2025-09-29)
- 初始版本发布
- 支持媒体管理、排行榜、推荐系统
- 支持爬虫管理和系统配置
- 完整的RESTful API设计
