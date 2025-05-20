import re
import logging
import requests
from bs4 import BeautifulSoup

# 设置日志记录器
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger = setup_logger()

# 提取最新视频链接
def get_latest_video_link(channel_url):
    try:
        logger.info(f"开始处理频道: {channel_url}")
        headers = {'User-Agent': 'Mozilla/.'}
        response = requests.get(channel_url, headers=headers, timeout=0)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # 搜索日期格式，假设日期格式为“YYYY年MM月DD日”
        date_pattern = re.compile(r'\d{}年\d{,}月\d{,}日')
        dates = soup.find_all(string=date_pattern)
        
        if not dates:
            logger.warning("未找到日期元素")
            return None
        
        # 取最新日期（列表最后一个元素），因为BeautifulSoup按文档顺序查找
        latest_date_str = str(dates[-])
        latest_date_pos = soup.get_text().find(latest_date_str)
        
        if latest_date_pos == -:
            logger.error("日期位置查找失败")
            return None
        
        # 在最新日期附近搜索/watch?v=
        watch_pattern = re.compile(r'/watch\?v=[^&"]+')
        match = watch_pattern.search(soup.get_text(), latest_date_pos)
        
        if not match:
            logger.warning("在日期附近未找到/watch?v=")
            return None
        
        watch_query = match.group()
        video_link = f"https://www.youtube.com/{watch_query}"
        logger.info(f"找到最新视频链接: {video_link}")
        return video_link
        
    except requests.RequestException as e:
        logger.error(f"网络请求异常: {str(e)}")
    except Exception as e:
        logger.error(f"处理异常: {str(e)}", exc_info=True)
    return None

# 主程序入口
if __name__ == '__main__':
    channel_url = "https://www.youtube.com/@ZYFXS"  # 替换为实际频道URL
    latest_video_link = get_latest_video_link(channel_url)
    if latest_video_link:
        print(f"最新视频链接: {latest_video_link}")
    else:
        print("未找到最新视频链接")
