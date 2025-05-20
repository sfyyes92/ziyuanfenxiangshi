import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_latest_date_video_url(channel_url):
    try:
        # 获取YouTube频道页面
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找所有视频链接（实际中可能需要调整选择器）
        video_elements = soup.find_all('a', {'id': 'video-title-link'})  # YouTube可能动态生成，需验证

        # 提取视频标题和链接，并过滤出以日期开头的视频
        date_videos = []
        date_pattern = re.compile(r'^\d{4}年\d{1,2}月\d{1,2}日')

        for video in video_elements:
            title = video.get('title', '')
            if date_pattern.match(title):
                video_url = 'https://www.youtube.com' + video['href'].split('&')[0]  # 清理多余参数
                date_str = title.split('日')[0] + '日'  # 提取日期部分
                try:
                    # 将中文日期转换为datetime对象便于比较
                    date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                    date_videos.append((date_obj, video_url, title))
                except ValueError:
                    continue

        if not date_videos:
            return None

        # 按日期降序排序并返回最新的
        latest_video = sorted(date_videos, key=lambda x: x[0], reverse=True)[0]
        return latest_video[1]  # 返回URL

    except Exception as e:
        print(f"Error: {e}")
        return None

# 示例使用
channel_url = "https://www.youtube.com/@ZYFXS"
latest_url = get_latest_date_video_url(channel_url)
print(f"Latest dated video URL: {latest_url}")
