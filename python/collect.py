import requests
import re

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
    date_pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    
    # 最终结果存储
    video_links = []
    
    # 查找所有日期出现的位置
    for date_match in date_pattern.finditer(html_content):
        date_str = date_match.group()
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
        
        video_links.append((date_str, full_url))
    
    return video_links

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    print(f"正在提取 {channel_url} 中的视频链接...")
    
    videos = extract_youtube_links(channel_url)
    
    if videos:
        print(f"找到 {len(videos)} 个视频:")
        for i, (date_str, url) in enumerate(videos, 1):
            print(f"{i}. 日期: {date_str}")
            print(f"   链接: {url}")
    else:
        print("没有找到符合条件的视频")
