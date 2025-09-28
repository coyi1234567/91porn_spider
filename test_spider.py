#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

from spider91 import Spider91
import logging

# 设置日志级别
logging.basicConfig(level=logging.INFO)

def test_basic_functionality():
    """测试基本功能"""
    print("=== 测试基本功能 ===")
    
    # 创建爬虫实例
    spider = Spider91(save_path="./test_videos")
    print("✅ 爬虫实例创建成功")
    
    # 测试数据库功能
    test_viewkey = "test123"
    is_downloaded = spider.is_downloaded(test_viewkey)
    print(f"✅ 数据库查询功能正常: {is_downloaded}")
    
    # 测试标记下载
    spider.mark_downloaded(test_viewkey, "测试视频", "http://test.com")
    is_downloaded_after = spider.is_downloaded(test_viewkey)
    print(f"✅ 数据库写入功能正常: {is_downloaded_after}")
    
    # 测试Chrome驱动
    driver = spider.get_chrome_driver()
    if driver:
        print("✅ Chrome驱动创建成功")
        driver.quit()
    else:
        print("❌ Chrome驱动创建失败")
    
    print("=== 基本功能测试完成 ===")

def test_config_loading():
    """测试配置文件加载"""
    print("\n=== 测试配置文件加载 ===")
    
    try:
        import yaml
        with open('proxyConfig.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            proxy_urls = config.get('ProxyUrls', [])
            print(f"✅ 代理配置加载成功: {len(proxy_urls)} 个代理")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
    
    try:
        with open('score/wordValue.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ 关键词配置文件加载成功: {len(content)} 字符")
    except Exception as e:
        print(f"❌ 关键词配置文件加载失败: {e}")
    
    try:
        with open('score/ownValue.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✅ 作者配置文件加载成功: {len(content)} 字符")
    except Exception as e:
        print(f"❌ 作者配置文件加载失败: {e}")
    
    print("=== 配置文件测试完成 ===")

def test_web_scraping():
    """测试网页抓取功能（使用测试网站）"""
    print("\n=== 测试网页抓取功能 ===")
    
    spider = Spider91()
    
    # 测试一个公开的测试网站
    test_url = "https://httpbin.org/html"
    
    try:
        driver = spider.get_chrome_driver()
        if driver:
            driver.get(test_url)
            title = driver.title
            print(f"✅ 网页访问成功: {title}")
            driver.quit()
        else:
            print("❌ 无法创建Chrome驱动")
    except Exception as e:
        print(f"❌ 网页抓取测试失败: {e}")
    
    print("=== 网页抓取测试完成 ===")

if __name__ == "__main__":
    print("开始测试Python爬虫...")
    
    test_basic_functionality()
    test_config_loading()
    test_web_scraping()
    
    print("\n🎉 所有测试完成！")
