#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
91porn视频爬虫 - Python版本
基于原始Go项目重写，支持视频爬取、下载、评分和去重功能

作者: AI Assistant
版本: 1.0.0
"""

import os
import sys
import time
import sqlite3
import logging
import subprocess
import yaml
import jieba
import re
import hashlib
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import chromedriver_autoinstaller

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spider91.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoInfo:
    """视频信息类"""
    def __init__(self):
        self.title = ""           # 视频标题
        self.url = ""            # 视频页面URL
        self.viewkey = ""        # 视频唯一标识
        self.duration = ""       # 视频时长
        self.author = ""         # 作者
        self.upload_time = ""    # 上传时间
        self.views = 0           # 观看次数
        self.rating = 0.0        # 评分
        self.score = 0           # 计算得分
        self.video_url = ""      # 视频下载URL
        self.heat = 0            # 热度
        self.favorites = 0       # 收藏数量
        self.comments = 0        # 评论数量
        self.likes = 0           # 点赞数
        self.dislikes = 0        # 踩数

class Spider91:
    """91porn爬虫主类"""
    
    def __init__(self, save_path="./videos_storage"):
        """
        初始化爬虫
        
        Args:
            save_path (str): 视频保存路径
        """
        self.save_path = save_path
        self.proxy_url = None
        self.word_scores = {}    # 关键词评分
        self.author_scores = {}  # 作者评分
        
        # 创建存储目录结构
        self.create_storage_structure()
        
        # 初始化数据库
        self.init_database()
        
        # 加载配置文件
        self.load_configs()
        
        logger.info("爬虫初始化完成")

    def create_storage_structure(self):
        """创建存储目录结构"""
        directories = [
            self.save_path,
            os.path.join(self.save_path, "daily"),
            os.path.join(self.save_path, "weekly"), 
            os.path.join(self.save_path, "monthly"),
            os.path.join(self.save_path, "custom"),
            os.path.join(self.save_path, "metadata")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info("存储目录结构创建完成")

    def init_database(self):
        """初始化SQLite数据库"""
        try:
            # 连接数据库
            self.db_path = os.path.join(self.save_path, "metadata", "videos.db")
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # 创建视频信息表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    viewkey TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT,
                    duration TEXT,
                    upload_time TEXT,
                    views INTEGER,
                    rating REAL,
                    score INTEGER,
                    heat INTEGER,
                    favorites INTEGER,
                    comments INTEGER,
                    likes INTEGER,
                    dislikes INTEGER,
                    video_url TEXT,
                    file_path TEXT,
                    file_size INTEGER,
                    file_hash TEXT,
                    download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rank_type TEXT,
                    rank_date TEXT,
                    rank_position INTEGER
                )
            ''')
            
            # 创建索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_viewkey ON videos(viewkey)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON videos(file_hash)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_download_time ON videos(download_time)')
            
            self.conn.commit()
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")

    def load_configs(self):
        """加载配置文件"""
        try:
            # 加载代理配置
            if os.path.exists("proxyConfig.yaml"):
                with open("proxyConfig.yaml", 'r', encoding='utf-8') as f:
                    proxy_config = yaml.safe_load(f)
                    if proxy_config and 'proxy_url' in proxy_config:
                        self.proxy_url = proxy_config['proxy_url']
                        logger.info(f"加载代理配置: {self.proxy_url}")
            
            # 加载关键词评分
            if os.path.exists("score/wordValue.txt"):
                with open("score/wordValue.txt", 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line:
                            word, score = line.split('=', 1)
                            self.word_scores[word.strip()] = int(score.strip())
                logger.info(f"加载了 {len(self.word_scores)} 个关键词评分")
            
            # 加载作者评分
            if os.path.exists("score/ownValue.txt"):
                with open("score/ownValue.txt", 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line:
                            author, score = line.split('=', 1)
                            self.author_scores[author.strip()] = int(score.strip())
                logger.info(f"加载了 {len(self.author_scores)} 个作者评分")
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")

    def is_downloaded(self, viewkey):
        """检查视频是否已下载"""
        try:
            self.cursor.execute("SELECT viewkey FROM videos WHERE viewkey = ?", (viewkey,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查下载状态失败: {e}")
            return False

    def get_file_hash(self, filepath):
        """计算文件MD5值"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"计算文件hash失败: {e}")
            return None

    def is_duplicate_file(self, file_hash):
        """检查文件是否重复（基于hash）"""
        try:
            self.cursor.execute("SELECT viewkey FROM videos WHERE file_hash = ?", (file_hash,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"检查文件重复失败: {e}")
            return False

    def save_video_metadata(self, video_info, filepath, rank_type, rank_date, rank_position):
        """保存视频元数据到数据库"""
        try:
            file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            file_hash = self.get_file_hash(filepath) if os.path.exists(filepath) else None
            
            self.cursor.execute('''
                INSERT OR REPLACE INTO videos 
                (viewkey, title, author, duration, upload_time, views, rating, score, 
                 heat, favorites, comments, likes, dislikes,
                 video_url, file_path, file_size, file_hash, rank_type, rank_date, rank_position)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_info.viewkey, video_info.title, video_info.author, video_info.duration,
                video_info.upload_time, video_info.views, video_info.rating, video_info.score,
                video_info.heat, video_info.favorites, video_info.comments, video_info.likes, video_info.dislikes,
                video_info.video_url, filepath, file_size, file_hash,
                rank_type, rank_date, rank_position
            ))
            
            self.conn.commit()
            logger.info(f"视频元数据已保存: {video_info.title}")
            
        except Exception as e:
            logger.error(f"保存视频元数据失败: {e}")

    def save_rank_metadata(self, videos, rank_type, rank_date):
        """保存榜单元数据到JSON文件"""
        try:
            metadata = {
                "rank_type": rank_type,
                "rank_date": rank_date,
                "total_videos": len(videos),
                "download_time": datetime.now().isoformat(),
                "videos": []
            }
            
            for i, video in enumerate(videos):
                video_meta = {
                    "rank": i + 1,
                    "viewkey": video.viewkey,
                    "title": video.title,
                    "author": video.author,
                    "score": video.score,
                    "views": video.views,
                    "duration": video.duration,
                    "heat": video.heat,
                    "favorites": video.favorites,
                    "comments": video.comments,
                    "likes": video.likes,
                    "dislikes": video.dislikes
                }
                metadata["videos"].append(video_meta)
            
            # 保存到JSON文件
            json_filename = f"{rank_type}_{rank_date}.json"
            json_filepath = os.path.join(self.save_path, "metadata", json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"榜单元数据已保存: {json_filename}")
            
        except Exception as e:
            logger.error(f"保存榜单元数据失败: {e}")

    def get_chrome_driver(self):
        """获取Chrome驱动"""
        try:
            # 自动安装chromedriver
            chromedriver_autoinstaller.install()
            
            # Chrome选项
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置代理
            if self.proxy_url:
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            # 尝试连接远程调试端口
            try:
                driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome远程调试已运行")
                return driver
            except Exception as e:
                logger.warning(f"连接远程调试失败: {e}")
                return None
                
        except Exception as e:
            logger.error(f"获取Chrome驱动失败: {e}")
            return None

    def handle_age_verification(self, driver):
        """处理年龄验证页面"""
        try:
            # 等待年龄验证按钮出现
            age_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '我已满18岁') or contains(text(), 'I am 18+') or contains(text(), 'Enter')]"))
            )
            age_button.click()
            logger.info("已处理年龄验证")
            time.sleep(2)
        except TimeoutException:
            logger.info("未发现年龄验证页面")
        except Exception as e:
            logger.warning(f"处理年龄验证失败: {e}")

    def parse_video_page(self, video_url):
        """解析视频页面获取详细信息"""
        driver = None
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return None
            
            logger.info(f"解析视频页面: {video_url}")
            driver.get(video_url)
            time.sleep(3)
            
            # 处理年龄验证
            self.handle_age_verification(driver)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            video_info = VideoInfo()
            video_info.url = video_url
            
            # 提取viewkey
            if 'viewkey=' in video_url:
                video_info.viewkey = video_url.split('viewkey=')[1].split('&')[0]
            
            # 提取标题 - 尝试多种选择器
            title_found = False
            title_selectors = [
                "h4.text-info",
                "h1",
                ".well h4",
                ".well h3", 
                ".well h2",
                ".well h1",
                "h4",
                "h3",
                "h2",
                ".video-title",
                ".title"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = driver.find_element(By.CSS_SELECTOR, selector)
                    title_text = title_element.text.strip()
                    if title_text and len(title_text) > 3:  # 确保标题不为空且有一定长度
                        video_info.title = title_text
                        title_found = True
                        logger.info(f"使用选择器 '{selector}' 找到标题: {title_text}")
                        break
                except NoSuchElementException:
                    continue
            
            if not title_found:
                # 如果所有选择器都失败，尝试从页面源码中提取
                try:
                    page_source = driver.page_source
                    import re
                    # 尝试多种标题模式
                    title_patterns = [
                        r'<h4[^>]*class="[^"]*text-info[^"]*"[^>]*>(.*?)</h4>',
                        r'<h1[^>]*>(.*?)</h1>',
                        r'<h4[^>]*>(.*?)</h4>',
                        r'<h3[^>]*>(.*?)</h3>',
                        r'<h2[^>]*>(.*?)</h2>',
                        r'<title[^>]*>(.*?)</title>'
                    ]
                    
                    for pattern in title_patterns:
                        match = re.search(pattern, page_source, re.DOTALL | re.IGNORECASE)
                        if match:
                            title_text = match.group(1).strip()
                            # 清理HTML标签
                            title_text = re.sub(r'<[^>]+>', '', title_text)
                            if title_text and len(title_text) > 3:
                                video_info.title = title_text
                                title_found = True
                                logger.info(f"从页面源码找到标题: {title_text}")
                                break
                except Exception as e:
                    logger.warning(f"从页面源码提取标题失败: {e}")
            
            if not title_found:
                video_info.title = f"未知标题_{video_info.viewkey}"
                logger.warning(f"无法提取标题，使用默认标题: {video_info.title}")
            
            # 提取视频URL
            try:
                video_element = driver.find_element(By.CSS_SELECTOR, "video source")
                video_info.video_url = video_element.get_attribute("src")
            except NoSuchElementException:
                try:
                    # 尝试从页面源码中提取视频URL
                    page_source = driver.page_source
                    import re
                    video_url_match = re.search(r'<source src="([^"]+\.mp4[^"]*)"', page_source)
                    if video_url_match:
                        video_info.video_url = video_url_match.group(1)
                except Exception as e:
                    logger.warning(f"提取视频URL失败: {e}")
            
            # 提取其他信息 - 热度和收藏数量
            try:
                import re
                # 提取热度
                try:
                    heat_element = driver.find_element(By.XPATH, "//span[contains(text(), '热度')]/following-sibling::span")
                    heat_text = heat_element.text.strip()
                    heat_match = re.search(r'(\d+)', heat_text)
                    if heat_match:
                        video_info.heat = int(heat_match.group(1))
                except NoSuchElementException:
                    pass
                
                # 提取收藏数量
                try:
                    fav_element = driver.find_element(By.XPATH, "//span[contains(text(), '收藏')]/following-sibling::span")
                    fav_text = fav_element.text.strip()
                    fav_match = re.search(r'(\d+)', fav_text)
                    if fav_match:
                        video_info.favorites = int(fav_match.group(1))
                except NoSuchElementException:
                    pass
                
                # 提取评论数量
                try:
                    comment_element = driver.find_element(By.XPATH, "//span[contains(text(), '留言')]/following-sibling::span")
                    comment_text = comment_element.text.strip()
                    comment_match = re.search(r'(\d+)', comment_text)
                    if comment_match:
                        video_info.comments = int(comment_match.group(1))
                except NoSuchElementException:
                    pass
                
                # 提取点赞和踩数
                try:
                    like_elements = driver.find_elements(By.CSS_SELECTOR, ".fa-thumbs-up")
                    if like_elements:
                        like_text = like_elements[0].find_element(By.XPATH, "following-sibling::span").text.strip()
                        like_match = re.search(r'(\d+)', like_text)
                        if like_match:
                            video_info.likes = int(like_match.group(1))
                except NoSuchElementException:
                    pass
                
                try:
                    dislike_elements = driver.find_elements(By.CSS_SELECTOR, ".fa-thumbs-down")
                    if dislike_elements:
                        dislike_text = dislike_elements[0].find_element(By.XPATH, "following-sibling::span").text.strip()
                        dislike_match = re.search(r'(\d+)', dislike_text)
                        if dislike_match:
                            video_info.dislikes = int(dislike_match.group(1))
                except NoSuchElementException:
                    pass
                
                # 提取其他信息
                info_elements = driver.find_elements(By.CSS_SELECTOR, ".text-muted")
                for element in info_elements:
                    text = element.text.strip()
                    if "时长" in text or "Duration" in text:
                        video_info.duration = text
                    elif "作者" in text or "Author" in text:
                        video_info.author = text
                    elif "上传" in text or "Upload" in text:
                        video_info.upload_time = text
                    elif "观看" in text or "Views" in text:
                        views_match = re.search(r'(\d+)', text)
                        if views_match:
                            video_info.views = int(views_match.group(1))
                            
            except Exception as e:
                logger.warning(f"提取视频信息失败: {e}")
            
            # 计算评分
            video_info.score = self.calculate_score(video_info)
            
            logger.info(f"成功解析视频: {video_info.title}")
            return video_info
            
        except Exception as e:
            logger.error(f"解析视频页面失败: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def calculate_score(self, video_info):
        """计算视频评分"""
        score = 0
        
        # 关键词评分
        if video_info.title:
            words = jieba.lcut(video_info.title)
            for word in words:
                if word in self.word_scores:
                    score += self.word_scores[word]
        
        # 作者评分
        if video_info.author and video_info.author in self.author_scores:
            score += self.author_scores[video_info.author]
        
        # 观看次数评分
        if video_info.views > 10000:
            score += 5
        elif video_info.views > 5000:
            score += 3
        elif video_info.views > 1000:
            score += 1
        
        return score

    def crawl_page(self, page_url):
        """爬取页面上的所有视频"""
        videos = []
        try:
            driver = self.get_chrome_driver()
            if not driver:
                return videos
            
            logger.info(f"爬取页面: {page_url}")
            driver.get(page_url)
            time.sleep(3)
            
            # 处理年龄验证
            self.handle_age_verification(driver)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "well"))
            )
            
            # 获取所有视频链接的URL列表
            video_urls = []
            try:
                video_links = driver.find_elements(By.CSS_SELECTOR, ".well a")
                for link in video_links:
                    try:
                        href = link.get_attribute("href")
                        if href and "view_video.php" in href:
                            viewkey = href.split('viewkey=')[1].split('&')[0]
                            if not self.is_downloaded(viewkey):
                                video_urls.append(href)
                    except Exception as e:
                        logger.warning(f"获取链接失败: {e}")
                        continue
            except Exception as e:
                logger.error(f"查找视频链接失败: {e}")
                driver.quit()
                return videos
            
            driver.quit()  # 关闭驱动，避免stale element问题
            
            # 逐个解析视频
            for url in video_urls:
                try:
                    video_info = self.parse_video_page(url)
                    if video_info:
                        videos.append(video_info)
                except Exception as e:
                    logger.error(f"解析视频失败 {url}: {e}")
                    continue
            
            logger.info(f"从页面 {page_url} 找到 {len(videos)} 个新视频")
            
        except Exception as e:
            logger.error(f"爬取页面失败 {page_url}: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return videos

    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        # 限制长度
        if len(filename) > 100:
            filename = filename[:100]
        return filename

    def get_date_string(self, date_type):
        """获取日期字符串"""
        now = datetime.now()
        if date_type == "daily":
            return now.strftime("%Y%m%d")
        elif date_type == "weekly":
            # 获取本周一的日期
            monday = now - timedelta(days=now.weekday())
            return monday.strftime("%Y%m%d")
        elif date_type == "monthly":
            return now.strftime("%Y%m")
        return now.strftime("%Y%m%d")

    def download_video(self, video_info, date_type="daily", rank=0):
        """下载视频"""
        try:
            if not video_info.video_url:
                logger.error(f"视频URL为空: {video_info.title}")
                return False
            
            # 创建存储路径
            date_str = self.get_date_string(date_type)
            rank_dir = os.path.join(self.save_path, date_type, date_str)
            os.makedirs(rank_dir, exist_ok=True)
            
            # 创建带分数、热度、收藏和日期的文件名
            safe_title = self.sanitize_filename(video_info.title)
            filename = f"[{date_type.upper()}_{date_str}]_RANK{rank+1:02d}_SCORE{video_info.score:03d}_HEAT{video_info.heat:06d}_FAV{video_info.favorites:04d}_{safe_title}_{video_info.viewkey}.mp4"
            filepath = os.path.join(rank_dir, filename)
            
            if os.path.exists(filepath):
                logger.info(f"视频已存在: {filename}")
                # 保存元数据
                self.save_video_metadata(video_info, filepath, date_type, date_str, rank+1)
                return True
            
            logger.info(f"开始下载: {video_info.title}")
            
            # 使用curl下载，添加必要的headers
            cmd = [
                "curl", "-L", 
                "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "-H", "Referer: https://91porn.com/",
                "-o", filepath, 
                video_info.video_url
            ]
            
            if self.proxy_url:
                cmd.extend(["-x", self.proxy_url])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(filepath):
                # 检查文件大小
                file_size = os.path.getsize(filepath)
                if file_size > 1000:  # 大于1KB认为是有效文件
                    # 检查文件重复
                    file_hash = self.get_file_hash(filepath)
                    if file_hash and self.is_duplicate_file(file_hash):
                        logger.warning(f"检测到重复文件，删除: {filename}")
                        os.remove(filepath)
                        return False
                    
                    # 保存元数据
                    self.save_video_metadata(video_info, filepath, date_type, date_str, rank+1)
                    logger.info(f"下载完成: {filename} ({file_size:,} bytes)")
                    return True
                else:
                    logger.error(f"下载的文件太小: {filename} ({file_size} bytes)")
                    os.remove(filepath)
                    return False
            else:
                logger.error(f"下载失败: {video_info.title}, 返回码: {result.returncode}")
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                return False
            
        except Exception as e:
            logger.error(f"下载视频失败 {video_info.title}: {e}")
            return False

    def daily_crawl(self):
        """日榜爬取模式 - 下载前10个视频"""
        logger.info("开始日榜爬取...")
        
        # 爬取首页
        homepage_url = "https://91porn.com/index.php"
        videos = self.crawl_page(homepage_url)
        
        if not videos:
            logger.info("没有找到新视频")
            return
        
        # 按评分排序
        videos.sort(key=lambda x: x.score, reverse=True)
        top10_videos = videos[:10]
        
        # 下载前10个视频
        download_count = 0
        for i, video in enumerate(top10_videos):
            if self.download_video(video, "daily", i):
                download_count += 1
                logger.info(f"日榜第{i+1}名: {video.title} (分数: {video.score})")
            time.sleep(2)  # 避免请求过快
        
        # 保存榜单元数据
        date_str = self.get_date_string("daily")
        self.save_rank_metadata(top10_videos, "daily", date_str)
        
        logger.info(f"日榜爬取完成，下载了 {download_count} 个视频")

    def weekly_crawl(self):
        """周榜爬取模式 - 下载前10个视频"""
        logger.info("开始周榜爬取...")
        
        # 爬取多个页面
        urls = [
            "https://91porn.com/index.php",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=1",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=2"
        ]
        
        all_videos = []
        for url in urls:
            videos = self.crawl_page(url)
            all_videos.extend(videos)
            time.sleep(3)
        
        if not all_videos:
            logger.info("没有找到新视频")
            return
        
        # 按评分排序
        all_videos.sort(key=lambda x: x.score, reverse=True)
        top10_videos = all_videos[:10]
        
        # 下载前10个视频
        download_count = 0
        for i, video in enumerate(top10_videos):
            if self.download_video(video, "weekly", i):
                download_count += 1
                logger.info(f"周榜第{i+1}名: {video.title} (分数: {video.score})")
            time.sleep(2)
        
        # 保存榜单元数据
        date_str = self.get_date_string("weekly")
        self.save_rank_metadata(top10_videos, "weekly", date_str)
        
        logger.info(f"周榜爬取完成，下载了 {download_count} 个视频")

    def monthly_crawl(self):
        """月榜爬取模式 - 下载前10个视频"""
        logger.info("开始月榜爬取...")
        
        # 爬取更多页面获取月榜数据
        urls = [
            "https://91porn.com/index.php",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=1",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=2",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=3",
            "https://91porn.com/v.php?category=rf&viewtype=basic&page=4"
        ]
        
        all_videos = []
        for url in urls:
            videos = self.crawl_page(url)
            all_videos.extend(videos)
            time.sleep(3)
        
        if not all_videos:
            logger.info("没有找到新视频")
            return
        
        # 按评分排序
        all_videos.sort(key=lambda x: x.score, reverse=True)
        top10_videos = all_videos[:10]
        
        # 下载前10个视频
        download_count = 0
        for i, video in enumerate(top10_videos):
            if self.download_video(video, "monthly", i):
                download_count += 1
                logger.info(f"月榜第{i+1}名: {video.title} (分数: {video.score})")
            time.sleep(2)
        
        # 保存榜单元数据
        date_str = self.get_date_string("monthly")
        self.save_rank_metadata(top10_videos, "monthly", date_str)
        
        logger.info(f"月榜爬取完成，下载了 {download_count} 个视频")

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='91porn视频爬虫 - 日榜/周榜/月榜')
    parser.add_argument('-d', '--daily', action='store_true', help='日榜爬取模式 (前10个)')
    parser.add_argument('-w', '--weekly', action='store_true', help='周榜爬取模式 (前10个)')
    parser.add_argument('-m', '--monthly', action='store_true', help='月榜爬取模式 (前10个)')
    parser.add_argument('-c', '--crawl', action='store_true', help='爬取指定页面')
    parser.add_argument('-u', '--url', type=str, help='要爬取的页面URL')
    parser.add_argument('-s', '--save-path', type=str, default='./videos_storage', help='视频保存路径')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    spider = Spider91(save_path=args.save_path)
    
    try:
        if args.daily:
            spider.daily_crawl()
        elif args.weekly:
            spider.weekly_crawl()
        elif args.monthly:
            spider.monthly_crawl()
        elif args.crawl and args.url:
            videos = spider.crawl_page(args.url)
            if videos:
                # 按评分排序并下载前10个
                videos.sort(key=lambda x: x.score, reverse=True)
                download_count = 0
                for i, video in enumerate(videos[:10]):
                    if spider.download_video(video, "custom", i):
                        download_count += 1
                    time.sleep(2)
                logger.info(f"爬取完成，下载了 {download_count} 个视频")
            else:
                logger.info("没有找到新视频")
        else:
            print("请指定运行模式:")
            print("  -d (日榜) 或 -w (周榜) 或 -m (月榜)")
            print("  -c -u <URL> (爬取指定页面)")
    
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        spider.cleanup()

if __name__ == "__main__":
    main()
