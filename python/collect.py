
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

def extract_watch_context(page_content, date_element):
    """在找到日期元素后，查找/watch?v=并打印其后100个字符"""
    try:
        content_str = str(page_content)
        date_pos = content_str.find(str(date_element))
        if date_pos != -1:
            watch_pos = content_str.find('/watch?v=', date_pos)
            if watch_pos != -1:
                watch_context = content_str[watch_pos:watch_pos+100]
                logger.info(f"找到/watch上下文: {watch_context}")
                return watch_context
    except Exception as e:
        logger.error(f"上下文提取失败: {str(e)}")
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
        
        dated_elements = soup.find_all(string=date_pattern)
        logger.info(f"找到{len(dated_elements)}个日期元素")
        
        for element in dated_elements:
            watch_context = extract_watch_context(soup, element)
            if watch_context:
                print(f"/watch上下文内容: {watch_context}")
        
        return []
        
    except requests.RequestException as e:
        logger.error(f"网络请求异常: {str(e)}")
    except Exception as e:
        logger.error(f"处理异常: {str(e)}", exc_info=True)
    return []

if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@ZYFXS"
    get_videos_by_date(channel_url)
