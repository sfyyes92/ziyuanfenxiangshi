import requests
import re
from datetime import datetime
from urllib.parse import urljoin

def get_youtube_content(url):
    """获取YouTube页面内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    try:
        print(f"正在获取页面: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
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

def extract_paste_links(content):
    """
    按照指定方法精确查找paste.to链接
    搜索逻辑：
    1. 找到"下载地址：https://paste.to/"
    2. 向后查找，先遇到"..."就重新搜索
    3. 先遇到"\n（密码在上方youtube视频中口述）"就提取两者间的内容
    """
    print("正在按照指定方法查找paste.to链接...")
    
    # 定义关键字符串
    start_marker = "下载地址：https://paste.to/"
    ellipsis_marker = "..."
    password_marker = "\n（密码在上方youtube视频中口述）"
    
    links = []
    pos = 0
    
    while pos < len(content):
        # 查找起始标记
        start_pos = content.find(start_marker, pos)
        if start_pos == -1:
            break
        
        # 从起始位置开始查找两个可能的结束标记
        ellipsis_pos = content.find(ellipsis_marker, start_pos)
        password_pos = content.find(password_marker, start_pos)
        
        # 判断哪个标记先出现
        if password_pos != -1 and (ellipsis_pos == -1 or password_pos < ellipsis_pos):
            # 找到密码标记，提取完整链接
            link_end = password_pos
            full_url = content[start_pos + len("下载地址："):link_end].strip()
            links.append(full_url)
            pos = password_pos + len(password_marker)
        elif ellipsis_pos != -1:
            # 找到省略号，跳过继续搜索
            pos = ellipsis_pos + len(ellipsis_marker)
        else:
            # 两个标记都没找到，结束搜索
            break
    
    return links

def search_paste_links(video_url):
    """在视频页面搜索paste.to链接"""
    content = get_youtube_content(video_url)
    if not content:
        return []
    
    return extract_paste_links(content)

def main():
    channel_url = "https://www.youtube.com/@ZYFXS"
    
    print("正在查找最新视频...")
    latest_video = find_latest_video(channel_url)
    if not latest_video:
        print("未找到符合条件的视频")
        return
    
    print(f"\n找到最新视频: {latest_video['date_str']}")
    print(f"视频链接: {latest_video['url']}")
    
    print("\n正在按照指定方法搜索paste.to链接...")
    links = search_paste_links(latest_video['url'])
    
    if links:
        print("\n找到的完整paste.to链接:")
        for i, link in enumerate(links, 1):
            print(f"{i}. {link}")
    else:
        print("未找到paste.to链接")

if __name__ == "__main__":
    main()
