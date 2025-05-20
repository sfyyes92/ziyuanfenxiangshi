
import re
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 日志配置
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # 控制台日志格式
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.INFO)
    
    # 文件日志格式
    file_handler = logging.FileHandler('youtube_scraper.log')
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.DEBUG)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

logger = setup_logger()

def get_latest_dated_video(channel_url):
    try:
        logger.info(f"开始处理频道: {channel_url}")
        response = requests.get(channel_url)
        response.raise_for_status()
        logger.debug(f"HTTP响应状态: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        video_items = soup.find_all('a', {'id': 'video-title-link'})
        logger.info(f"找到{len(video_items)}个视频元素")
        
        date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
        dated_videos = []
        
        for idx, item in enumerate(video_items):
            try:
                title = item.get('title', '')
                logger.debug(f"正在检查第{idx+1}个视频: {title[:30]}...")
                
                match = date_pattern.match(title)
                if match:
                    year, month, day = map(int, match.groups())
                    video_date = datetime(year, month, day)
                    video_url = 'https://www.youtube.com' + item['href']
                    dated_videos.append((video_date, video_url, title))
                    logger.info(f"发现日期格式视频: {video_date} - {title[:20]}...")
            
            except Exception as e:
                logger.error(f"处理第{idx+1}个视频时出错: {str(e)}", exc_info=True)
        
        if dated_videos:
            dated_videos.sort(reverse=True)
            latest = dated_videos[0][1]
            logger.info(f"找到最新视频: {latest}")
            return latest
        
        logger.warning("未找到符合日期格式的视频")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"网络请求失败: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"程序发生未预期错误: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        channel_url = "https://www.youtube.com/@ZYFXS"
        latest_video = get_latest_dated_video(channel_url)
        print(f"最新视频链接: {latest_video}")
    except Exception:
        logger.exception("主程序执行失败")
