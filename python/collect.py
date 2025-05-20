import requests
from bs4 import BeautifulSoup
import re

def find_youtube_links_by_date(channel_url, target_date):
    # 发送HTTP请求获取页面内容
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"无法访问页面: {e}")
        return []
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找包含目标日期的文本
    date_pattern = re.escape(target_date)
    pattern = re.compile(f'{date_pattern}.*?/watch\\?v=([^"]+)')
    
    # 查找所有匹配的视频ID
    matches = pattern.findall(response.text)
    
    # 构建完整的视频链接
    video_links = [f'https://www.youtube.com/watch?v={vid}' for vid in matches]
    
    return list(set(video_links))  # 去重

if __name__ == "__main__":
    # 目标频道
    channel_url = "https://www.youtube.com/@ZYFXS"
    
    # 用户输入目标日期
    target_date = input("请输入要查找的日期(格式如: 2023年10月15日): ")
    
    print(f"正在查找 {target_date} 的视频链接...")
    
    # 查找并打印结果
    video_links = find_youtube_links_by_date(channel_url, target_date)
    
    if video_links:
        print(f"找到 {len(video_links)} 个视频链接:")
        for i, link in enumerate(video_links, 1):
            print(f"{i}. {link}")
    else:
        print("没有找到匹配的视频链接")
