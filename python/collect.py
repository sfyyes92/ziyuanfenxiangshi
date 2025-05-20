
import re
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    file_handler = logging.FileHandler('youtube_scraper.log')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

def extract_video_url(element):
    """从元素中提取视频URL"""
    for parent in element.parents:
        if parent.name == 'a' and 'href' in parent.attrs:
            return 'https://www.youtube.com' + parent['href']
    return None

def get_latest_dated_video(channel_url):
    try:
        logger.info(f"开始处理频道: {channel_url}")
        response = requests.get(channel_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        date_pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
        
        # 查找所有包含日期文本的元素
        date_elements = soup.find_all(string=date_pattern)
        logger.info(f"找到{len(date_elements)}个日期元素")
        
        videos = []
        for element in date_elements:
            try:
                date_text = element.strip()
                url = extract_video_url(element)
                if url:
                    match = date_pattern.match(date_text)
                    if match:
                        year, month, day = map(int, match.groups())
                        video_date = datetime(year, month, day)
                        videos.append((video_date, url, date_text))
                        logger.debug(f"发现视频: {date_text} -> {url}")
            except Exception as e:
                logger.error(f"处理元素时出错: {str(e)}", exc_info=True)
        
        if videos:
            videos.sort(reverse=True)
            latest_url = videos[0][1]
            logger.info(f"最新视频链接: {latest_url}")
            return latest_url
            
        logger.warning("未找到有效视频链接")
        return None
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@ZYFXS"
    print("最新视频链接:", get_latest_dated_video(channel_url))
