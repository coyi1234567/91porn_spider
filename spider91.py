#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import time
import schedule
import yaml
import sqlite3
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from fake_useragent import UserAgent
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spider91.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoInfo:
    def __init__(self, title, url, viewkey, duration, author, upload_time, views, rating):
        self.title = title
        self.url = url
        self.viewkey = viewkey
        self.duration = duration
        self.author = author
        self.upload_time = upload_time
        self.views = views
        self.rating = rating
        self.score = 0

class Spider91:
    def __init__(self, proxy_url=None, save_path="./videos"):
        self.proxy_url = proxy_url
        self.save_path = save_path
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # 设置代理
        if proxy_url:
            self.session.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
        
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)
        
        # 初始化数据库
        self.init_database()
        
        # 安装Chrome驱动
        chromedriver_autoinstaller.install()
    
    def init_database(self):
        """初始化SQLite数据库"""
        self.db_path = "doneDB/videos.db"
        os.makedirs("doneDB", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                viewkey TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def is_downloaded(self, viewkey):
        """检查视频是否已下载"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT viewkey FROM videos WHERE viewkey = ?", (viewkey,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def mark_downloaded(self, viewkey, title, url):
        """标记视频为已下载"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO videos (viewkey, title, url) VALUES (?, ?, ?)",
            (viewkey, title, url)
        )
        
        conn.commit()
        conn.close()
    
    def get_chrome_driver(self):
        """获取Chrome浏览器驱动"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        
        if self.proxy_url:
            chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"创建Chrome驱动失败: {e}")
            return None
    
    def parse_video_page(self, url):
        """解析单个视频页面"""
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return None
            
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 获取视频信息
            title = driver.find_element(By.CSS_SELECTOR, "h4").text
            viewkey = url.split('viewkey=')[1].split('&')[0]
            
            # 获取视频下载链接
            video_elements = driver.find_elements(By.TAG_NAME, "video")
            video_url = None
            
            if video_elements:
                video_url = video_elements[0].get_attribute("src")
            
            driver.quit()
            
            if video_url:
                return {
                    'title': title,
                    'viewkey': viewkey,
                    'video_url': video_url,
                    'page_url': url
                }
            
        except Exception as e:
            logger.error(f"解析视频页面失败 {url}: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return None
    
    def crawl_page(self, page_url):
        """爬取页面上的所有视频"""
        videos = []
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return videos
            
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "well"))
            )
            
            # 查找所有视频链接
            video_links = driver.find_elements(By.CSS_SELECTOR, ".well a")
            
            for link in video_links:
                href = link.get_attribute("href")
                if href and "view_video.php" in href:
                    viewkey = href.split('viewkey=')[1].split('&')[0]
                    
                    if not self.is_downloaded(viewkey):
                        video_info = self.parse_video_page(href)
                        if video_info:
                            videos.append(video_info)
            
            driver.quit()
            logger.info(f"从页面 {page_url} 找到 {len(videos)} 个新视频")
            
        except Exception as e:
            logger.error(f"爬取页面失败 {page_url}: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return videos
    
    def download_video(self, video_info):
        """下载视频"""
        try:
            filename = f"{video_info['viewkey']}.mp4"
            filepath = os.path.join(self.save_path, filename)
            
            if os.path.exists(filepath):
                logger.info(f"视频已存在: {filename}")
                return True
            
            response = self.session.get(video_info['video_url'], stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 标记为已下载
            self.mark_downloaded(
                video_info['viewkey'],
                video_info['title'],
                video_info['page_url']
            )
            
            logger.info(f"下载完成: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"下载视频失败 {video_info['title']}: {e}")
            return False
    
    def daily_crawl(self):
        """日常爬取模式"""
        logger.info("开始日常爬取...")
        
        # 爬取前几页的最新视频
        for page in range(1, 4):
            page_url = f"http://91porn.com/v.php?category=rf&viewtype=basic&page={page}"
            videos = self.crawl_page(page_url)
            
            for video in videos[:10]:  # 每页最多下载10个
                self.download_video(video)
                time.sleep(2)  # 避免请求过快
    
    def weekly_crawl(self):
        """周度爬取模式"""
        logger.info("开始周度爬取...")
        
        # 创建周度文件夹
        week_folder = f"week_{datetime.now().strftime('%Y_%W')}"
        week_path = os.path.join(self.save_path, week_folder)
        os.makedirs(week_path, exist_ok=True)
        
        # 爬取更多页面
        for page in range(1, 6):
            page_url = f"http://91porn.com/v.php?category=rf&viewtype=basic&page={page}"
            videos = self.crawl_page(page_url)
            
            for video in videos:
                # 保存到周度文件夹
                original_path = self.save_path
                self.save_path = week_path
                self.download_video(video)
                self.save_path = original_path
                time.sleep(2)

def load_config():
    """加载配置文件"""
    try:
        with open('proxyConfig.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('ProxyUrls', [])
    except FileNotFoundError:
        logger.warning("配置文件 proxyConfig.yaml 不存在")
        return []

def main():
    parser = argparse.ArgumentParser(description='91视频网站爬虫工具')
    parser.add_argument('-c', '--crawl', action='store_true', help='爬取模式')
    parser.add_argument('-u', '--url', help='爬取的网页URL')
    parser.add_argument('-o', '--output', default='./videos', help='视频存储路径')
    parser.add_argument('-p', '--proxy', help='代理地址')
    parser.add_argument('-t', '--threads', type=int, default=3, help='同时爬取的视频个数')
    parser.add_argument('-now', '--days', type=int, help='爬取前X天的视频')
    parser.add_argument('-n', '--number', type=int, help='爬取前X个视频')
    
    args = parser.parse_args()
    
    # 获取代理列表
    proxy_urls = load_config()
    if args.proxy:
        proxy_urls = [args.proxy]
    
    # 创建爬虫实例
    spider = Spider91(
        proxy_url=proxy_urls[0] if proxy_urls else None,
        save_path=args.output
    )
    
    if args.crawl and args.url:
        # 单个URL爬取模式
        if "view_video.php" in args.url:
            # 单个视频
            video_info = spider.parse_video_page(args.url)
            if video_info:
                spider.download_video(video_info)
        else:
            # 页面爬取
            videos = spider.crawl_page(args.url)
            for video in videos:
                spider.download_video(video)
                time.sleep(2)
    
    elif args.days and args.number:
        # 按天数和数量爬取
        logger.info(f"爬取前{args.days}天的前{args.number}个视频")
        # 这里可以实现更复杂的筛选逻辑
    
    else:
        # 定时任务模式
        logger.info("启动定时任务模式")
        
        # 每天8点执行日常爬取
        schedule.every().day.at("08:00").do(spider.daily_crawl)
        
        # 每周六9点执行周度爬取
        schedule.every().saturday.at("09:00").do(spider.weekly_crawl)
        
        # 立即执行一次
        spider.daily_crawl()
        
        # 保持程序运行
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
