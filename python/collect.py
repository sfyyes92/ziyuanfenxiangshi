import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

# 配置日志输出（方便调试）
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_latest_date_video_url(channel_url):
    try:
        logger.info(f"Fetching YouTube channel page: {channel_url}")
        
        # 1. 获取页面内容
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Page status code: {response.status_code}")
        
        # 2. 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 调试：保存HTML到文件（可选）
        with open("youtube_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        logger.info("HTML saved to 'youtube_page.html' for inspection.")
        
        # 3. 查找视频元素（调整选择器）
        # YouTube可能使用以下结构，但实际需根据HTML调整
        video_links = soup.find_all('a', href=re.compile(r'/watch\?v='))
        logger.info(f"Found {len(video_links)} potential video links.")
        
        # 4. 提取视频标题和日期
        date_pattern = re.compile(r'^\d{4}年\d{1,2}月\d{1,2}日')
        date_videos = []
        
        for link in video_links:
            title = link.get('title', '') or link.text.strip()
            href = link.get('href', '')
            
            if not title or not href:
                continue
                
            logger.debug(f"Checking video: {title} | {href}")
            
            # 检查标题是否以日期开头
            if date_pattern.match(title):
                video_url = f"https://www.youtube.com{href.split('&')[0]}"
                date_str = title.split('日')[0] + '日'
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                    date_videos.append((date_obj, video_url, title))
                    logger.info(f"Found dated video: {date_str} | {video_url}")
                except ValueError as e:
                    logger.warning(f"Failed to parse date from title: {title} | Error: {e}")
        
        # 5. 返回最新视频
        if not date_videos:
            logger.warning("No dated videos found!")
            return None
            
        latest_video = sorted(date_videos, key=lambda x: x[0], reverse=True)[0]
        logger.info(f"Latest video: {latest_video[1]} (Title: {latest_video[2]})")
        return latest_video[1]
        
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)
        return None

# 测试
if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    latest_url = get_latest_date_video_url(channel_url)
    print(f"\nFinal result: {latest_url}")
