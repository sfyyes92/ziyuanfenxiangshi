import requests
import re
from datetime import datetime
from urllib.parse import urljoin, unquote

def get_youtube_content(url):
    """获取YouTube页面内容（改进版）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        print(f"正在获取页面: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 检查内容是否完整
        if len(response.text) < 50000:
            print("警告：获取的内容可能不完整")
        
        return response.text
    except Exception as e:
        print(f"获取内容失败: {str(e)}")
        return None

def find_latest_video(channel_url):
    """查找最新日期的视频（保持不变）"""
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

def extract_full_paste_links(content):
    """
    改进的链接提取方法
    从页面源代码中提取完整的paste.to链接（包括被前端省略的部分）
    """
    print("正在从源代码中提取完整paste.to链接...")
    
    # 方法1：从JSON数据块中提取
    json_matches = re.finditer(
        r'"url":"(https?:\\/\\/paste\.to[^"]+)"',
        content
    )
    
    # 方法2：从HTML属性中提取
    html_matches = re.finditer(
        r'href=["\'](https?://paste\.to[^"\']+)["\']',
        content
    )
    
    # 合并结果并去重
    links = set()
    for match in list(json_matches) + list(html_matches):
        full_url = unquote(match.group(1)).replace('\\/', '/')
        links.add(full_url)
    
    return sorted(links)

def search_paste_links(video_url):
    """在视频页面搜索完整的paste.to链接"""
    content = get_youtube_content(video_url)
    if not content:
        return []
    
    # 保存原始内容供调试
    with open('video_page_source.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("已保存页面源代码到 video_page_source.html")
    
    return extract_full_paste_links(content)

def main():
    channel_url = "https://www.youtube.com/@ZYFXS"
    
    print("正在查找最新视频...")
    latest_video = find_latest_video(channel_url)
    if not latest_video:
        print("未找到符合条件的视频")
        return
    
    print(f"\n找到最新视频: {latest_video['date_str']}")
    print(f"视频链接: {latest_video['url']}")
    
    print("\n正在搜索paste.to链接...")
    links = search_paste_links(latest_video['url'])
    
    if links:
        print("\n找到的完整paste.to链接:")
        for i, link in enumerate(links, 1):
            print(f"{i}. {link}")
            
            # 提取密码部分（如果有）
            password_match = re.search(r'密码[：:]([^\s]+)', link)
            if password_match:
                print(f"   密码: {password_match.group(1)}")
    else:
        print("未找到paste.to链接")

if __name__ == "__main__":
    main()
