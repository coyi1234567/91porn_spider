# 代理设置指南

## 问题分析

测试结果显示：
- ❌ 所有常见代理端口都不可用 (10808, 1080, 7890, 8080, 10809, 10810)
- ❌ 直接访问91porn被拒绝 (ERR_CONNECTION_REFUSED)
- ✅ Chrome驱动和基本网络连接正常

## 解决方案

### 1. 启动代理服务

您需要先启动代理服务。常见的代理软件：

#### Clash/ClashX (推荐)
```bash
# 启动Clash
clash

# 或者使用ClashX (Mac GUI版本)
# 下载并安装ClashX，然后启动
```

#### V2Ray
```bash
# 启动V2Ray
v2ray

# 或者使用V2RayX (Mac GUI版本)
```

#### Shadowsocks
```bash
# 启动Shadowsocks
ss-local -c config.json
```

### 2. 检查代理端口

启动代理后，检查端口：
```bash
# 检查常见端口
netstat -an | grep 1080
netstat -an | grep 7890
netstat -an | grep 8080

# 或者使用lsof
lsof -i :1080
lsof -i :7890
```

### 3. 更新代理配置

编辑 `proxyConfig.yaml` 文件：
```yaml
ProxyUrls:
  - "http://127.0.0.1:7890"  # Clash默认端口
  - "http://127.0.0.1:1080"  # 其他代理默认端口
  - "http://127.0.0.1:10808" # 自定义端口
```

### 4. 测试代理连接

```bash
# 测试代理是否工作
curl --proxy http://127.0.0.1:7890 https://httpbin.org/ip

# 或者使用Python测试
python3 -c "
import requests
proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
response = requests.get('https://httpbin.org/ip', proxies=proxies)
print(response.json())
"
```

### 5. 重新测试爬虫

代理配置好后，重新运行测试：
```bash
source venv/bin/activate
python3 test_simple.py
```

## 常见问题

### Q: 代理启动后仍然无法访问
A: 检查以下几点：
1. 代理配置是否正确
2. 代理服务器是否可用
3. 防火墙是否阻止了连接
4. 代理软件的系统代理是否开启

### Q: 如何确认代理工作正常
A: 使用以下方法测试：
1. 浏览器访问 http://httpbin.org/ip 查看IP
2. 使用curl命令测试
3. 检查代理软件的日志

### Q: 代理端口不是默认端口
A: 修改 `proxyConfig.yaml` 文件中的端口号

## 下一步

1. 启动您的代理软件
2. 确认代理端口可用
3. 更新配置文件
4. 重新运行测试脚本

代理配置完成后，爬虫就可以正常工作了！
