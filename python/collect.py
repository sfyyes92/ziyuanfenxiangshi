
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

def extract_url_context(page_content, date_element):
    """在找到日期元素后，查找url字符串并打印其后100个字符"""
    try:
        content_str = str(page_content)
        date_pos = content_str.find(str(date_element))
        if date_pos != -1:
            url_pos = content_str.find('url', date_pos)
            if url_pos != -1:
                url_context = content_str[url_pos:url_pos+103]  # url(3) + 100
                logger.info(f"找到url上下文: {url_context}")
                return url_context
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
            url_context = extract_url_context(soup, element)
            if url_context:
                print(f"URL上下文内容: {url_context}")
        
        return []
        
    except requests.RequestException as e:
        logger.error(f"网络请求异常: {str(e)}")
    except Exception as e:
        logger.error(f"处理异常: {str(e)}", exc_info=True)
    return []

if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@ZYFXS"
    get_videos_by_date(channel_url)
