import requests
import re
from datetime import datetime
from urllib.parse import urljoin

def get_youtube_content(url):
    """获取YouTube页面内容并打印"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        print(f"正在获取页面: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 打印前2000个字符和后2000个字符
        content = response.text
        print("\n======= 页面内容开始 =======")
        print("【前2000字符】:")
        print(content[:2000])
        print("\n【后2000字符】:")
        print(content[-2000:])
        print("======= 页面内容结束 =======\n")
        
        return content
    except Exception as e:
        print(f"获取内容失败: {str(e)}")
        return None

def find_latest_video(channel_url):
    """查找最新日期的视频"""
    content = get_youtube_content(channel_url)
    if not content:
        return None

    # 匹配日期格式的视频
    date_pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日).*?"url":"(/watch\?v=[^"]+)"')
    matches = date_pattern.finditer(content)
    
    videos = []
    for match in matches:
        date_str = match.group(1)
        video_path = match.group(2)
        video_url = urljoin('https://www.youtube.com', video_path)
        
        try:
            date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
            videos.append({
                'date_str': date_str,
                'date_obj': date_obj,
                'url': video_url
            })
            print(f"找到视频: {date_str} - {video_url}")
        except ValueError:
            continue
    
    if not videos:
        return None
    
    # 按日期排序获取最新视频
    videos.sort(key=lambda x: x['date_obj'], reverse=True)
    return videos[0]

def debug_search_paste_links(content):
    """调试用：尝试多种方法查找paste.to链接"""
    print("\n======= 开始调试搜索 =======")
    
    # 方法1：直接搜索您提供的格式
    print("\n方法1：搜索'下载地址：https://paste.to/'")
    matches = re.finditer(r'下载地址：\s*(https?://paste\.to/[^\s]+)', content)
    for i, match in enumerate(matches, 1):
        print(f"找到链接{i}: {match.group(1)}")
    
    # 方法2：搜索包含哈希的paste.to链接
    print("\n方法2：搜索带哈希的paste.to链接")
    matches = re.finditer(r'(https?://paste\.to/\?[a-f0-9]+#[^\s"<]+)', content)
    for i, match in enumerate(matches, 1):
        print(f"找到链接{i}: {match.group(1)}")
    
    # 方法3：搜索包含"paste.to"的行
    print("\n方法3：搜索包含'paste.to'的行")
    lines = content.split('\n')
    for line in lines:
        if 'paste.to' in line:
            print(f"找到相关行: {line[:200]}...")  # 只打印前200字符
    
    print("======= 调试搜索结束 =======\n")

def main():
    channel_url = "https://www.youtube.com/@ZYFXS"
    
    print("正在查找最新视频...")
    latest_video = find_latest_video(channel_url)
    if not latest_video:
        print("未找到符合条件的视频")
        return
    
    print(f"\n找到最新视频: {latest_video['date_str']}")
    print(f"视频链接: {latest_video['url']}")
    
    print("\n正在获取视频页面内容...")
    content = get_youtube_content(latest_video['url'])
    if not content:
        print("无法获取页面内容")
        return
    
    # 调试搜索
    debug_search_paste_links(content)
    
    # 保存完整内容供检查
    with open('debug_video_content.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("已保存完整内容到 debug_video_content.txt")

if __name__ == "__main__":
    main()
