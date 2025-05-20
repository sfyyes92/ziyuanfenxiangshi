
import re
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    file_handler = logging.FileHandler('youtube_scraper.log')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

def extract_video_data(element):
    """提取视频URL和日期数据"""
    try:
        # 查找最近的<a>标签获取URL
        url_tag = element.find_parent('a', href=re.compile(r'/watch\?v='))
        if url_tag:
            raw_url = url_tag['href'].replace('\\u0026', '&')
            return {
                'url': f"https://www.youtube.com{raw_url.split('&pp=')[0]}",
                'date_text': element.get_text().strip()
            }
    except Exception as e:
        logger.error(f"元素解析失败: {str(e)}")
    return None

def get_videos_by_date(channel_url):
    try:
        logger.info(f"开始处理频道: {channel_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(channel_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        date_pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        
        # 查找所有包含日期的元素
        dated_elements = soup.find_all(string=date_pattern)
        logger.info(f"找到{len(dated_elements)}个日期元素")
        
        videos = []
        for element in dated_elements:
            video_data = extract_video_data(element)
            if video_data:
                try:
                    date_match = date_pattern.search(video_data['date_text'])
                    if date_match:
                        date_obj = datetime.strptime(date_match.group(), '%Y年%m月%d日')
                        videos.append((date_obj, video_data['url']))
                except ValueError as e:
                    logger.warning(f"日期解析失败: {video_data['date_text']} - {str(e)}")
        
        if videos:
            videos.sort(reverse=True)
            logger.info(f"成功获取{len(videos)}个视频链接")
            return [url for _, url in videos]
            
        logger.warning("未提取到有效视频数据")
        return []
        
    except requests.RequestException as e:
        logger.error(f"网络请求异常: {str(e)}")
    except Exception as e:
        logger.error(f"处理异常: {str(e)}", exc_info=True)
    return []

if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@ZYFXS"
    video_links = get_videos_by_date(channel_url)
    print("提取到的视频链接:", video_links)
