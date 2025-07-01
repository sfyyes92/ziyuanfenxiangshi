import requests
import re
from datetime import datetime
from urllib.parse import urljoin, unquote, parse_qs

def get_youtube_content(url):
    """获取YouTube页面内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
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
        except ValueError:
            continue
    
    if not videos:
        return None
    
    # 按日期排序获取最新视频
    videos.sort(key=lambda x: x['date_obj'], reverse=True)
    return videos[0]

def extract_paste_from_redirect(redirect_url):
    """从YouTube重定向URL中提取paste.to真实链接"""
    try:
        # 解析查询参数
        params = parse_qs(redirect_url.split('?', 1)[1])
        encoded_url = params.get('q', [''])[0]
        
        if not encoded_url:
            return None
            
        # URL解码
        decoded_url = unquote(encoded_url)
        
        # 提取完整的paste.to链接（去除可能的后续参数）
        paste_match = re.search(r'(https?://paste\.to/[^\s&]+)', decoded_url)
        return paste_match.group(1) if paste_match else None
    except Exception:
        return None

def find_all_paste_links(content):
    """综合查找所有paste.to链接（直接+重定向）"""
    links = set()
    
    # 方法1：直接查找显式链接
    direct_matches = re.finditer(
        r'(?:下载地址：|地址：)\s*(https?://paste\.to/[^\s<"]+)', 
        content
    )
    for match in direct_matches:
        links.add(match.group(1).strip())
    
    # 方法2：从重定向URL中提取
    redirect_matches = re.finditer(
        r'https://www\.youtube\.com/redirect\?[^\s"<]+', 
        content
    )
    for match in redirect_matches:
        if paste_link := extract_paste_from_redirect(match.group()):
            links.add(paste_link)
    
    return sorted(links)

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
    
    print("正在搜索paste.to链接...")
    paste_links = find_all_paste_links(content)
    
    if paste_links:
        print("\n找到的paste.to链接:")
        for i, link in enumerate(paste_links, 1):
            print(f"{i}. {link}")
    else:
        print("\n未找到paste.to链接")

if __name__ == "__main__":
    main()
