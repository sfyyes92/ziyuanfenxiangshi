import requests
import re
from datetime import datetime

def extract_youtube_links(channel_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"无法访问页面: {e}")
        return []

    # 匹配年月日格式（如：2023年10月15日）
    date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
    
    video_links = []
    
    # 查找所有日期出现的位置
    for date_match in date_pattern.finditer(html_content):
        year, month, day = map(int, date_match.groups())
        date_str = date_match.group()
        date_obj = datetime(year, month, day)
        date_end_pos = date_match.end()
        
        # 在日期后查找/watch?v=
        watch_pos = html_content.find('/watch?v=', date_end_pos)
        if watch_pos == -1:
            continue
        
        # 查找/watch?v=后面的引号
        quote_pos = html_content.find('"', watch_pos)
        if quote_pos == -1:
            continue
        
        # 提取/watch?v=...这部分
        watch_part = html_content[watch_pos:quote_pos]
        full_url = f'https://www.youtube.com{watch_part}'
        
        video_links.append({
            'date_str': date_str,
            'date_obj': date_obj,
            'url': full_url
        })
    
    return video_links

def find_latest_video(video_links):
    if not video_links:
        return None
    
    # 按日期从新到旧排序
    sorted_videos = sorted(video_links, key=lambda x: x['date_obj'], reverse=True)
    return sorted_videos[0]

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    print(f"正在提取 {channel_url} 中的视频链接...")
    
    videos = extract_youtube_links(channel_url)
    
    if videos:
        print(f"找到 {len(videos)} 个日期视频链接")
        
        # 找出最新日期的视频
        latest_video = find_latest_video(videos)
        
        print("\n最新日期的视频:")
        print(f"日期: {latest_video['date_str']}")
        print(f"链接: {latest_video['url']}")
        
        # 打印所有找到的日期和链接（按日期排序）
        print("\n所有找到的视频（按日期排序）:")
        sorted_videos = sorted(videos, key=lambda x: x['date_obj'], reverse=True)
        for i, video in enumerate(sorted_videos, 1):
            print(f"{i}. 日期: {video['date_str']}")
            print(f"   链接: {video['url']}")
    else:
        print("没有找到符合条件的视频")
