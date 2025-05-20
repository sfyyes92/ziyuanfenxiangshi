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
        print(f"无法访问频道页面: {e}")
        return None

    date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
    video_links = []
    
    for date_match in date_pattern.finditer(html_content):
        year, month, day = map(int, date_match.groups())
        date_str = date_match.group()
        date_obj = datetime(year, month, day)
        date_end_pos = date_match.end()
        
        watch_pos = html_content.find('/watch?v=', date_end_pos)
        if watch_pos == -1:
            continue
        
        quote_pos = html_content.find('"', watch_pos)
        if quote_pos == -1:
            continue
        
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
    return sorted(video_links, key=lambda x: x['date_obj'], reverse=True)[0]

def extract_download_link(video_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(video_url, headers=headers)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"无法访问视频页面: {e}")
        return None

    # 查找所有"下载地址：https://paste.to/"出现的位置
    download_markers = [m.start() for m in re.finditer('下载地址：https://paste\.to/', html_content)]
    
    for marker_pos in download_markers:
        # 从标记位置开始查找换行密码提示
        password_pos = html_content.find('\n（密码在上方youtube视频中口述）', marker_pos)
        
        # 检查两者之间是否有>字符
        if password_pos == -1:
            continue
            
        between_content = html_content[marker_pos:password_pos]
        if '>' in between_content:
            continue
            
        # 提取https://paste.to/...这部分（直到换行符前）
        start = html_content.find('https://paste.to/', marker_pos)
        end = html_content.find('\n', start)
        
        if start != -1 and end != -1:
            return html_content[start:end]
    
    return None

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    print(f"正在处理频道: {channel_url}")
    
    # 第一步：获取频道中最新的视频
    videos = extract_youtube_links(channel_url)
    
    if not videos:
        print("没有找到任何日期视频")
        exit()
        
    latest_video = find_latest_video(videos)
    print(f"\n找到最新视频: {latest_video['date_str']}")
    print(f"视频链接: {latest_video['url']}")
    
    # 第二步：从视频页面提取下载地址
    print("\n正在从视频页面提取下载地址...")
    download_link = extract_download_link(latest_video['url'])
    
    if download_link:
        print("\n成功找到下载地址:")
        print(download_link)
    else:
        print("\n没有找到符合条件的下载地址")
