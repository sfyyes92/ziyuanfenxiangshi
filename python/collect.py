import requests
from bs4 import BeautifulSoup
import re

def extract_date_video_links(channel_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"无法访问页面: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 匹配日期格式（如：2023年10月15日）
    date_pattern = re.compile(r'\d{4}年\d{1,2}月\d{1,2}日')
    
    video_links = []
    
    # 查找所有视频链接元素
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/watch?v=' in href:
            # 获取视频标题
            title = link.get('title', '') or link.text.strip()
            
            # 检查标题是否以日期开头
            if date_pattern.match(title):
                video_id = href.split('watch?v=')[1].split('&')[0]
                full_url = f'https://www.youtube.com{href.split("&")[0]}'
                video_links.append((title, full_url))
    
    return video_links

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    print(f"正在提取 {channel_url} 中以日期开头的视频链接...")
    
    videos = extract_date_video_links(channel_url)
    
    if videos:
        print(f"找到 {len(videos)} 个以日期开头的视频:")
        for i, (title, url) in enumerate(videos, 1):
            print(f"{i}. {title}")
            print(f"   链接: {url}")
    else:
        print("没有找到以日期开头的视频")
