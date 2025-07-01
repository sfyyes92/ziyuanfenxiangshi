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

def extract_paste_link(content):
    """
    严格按照指定方法提取paste.to链接
    搜索逻辑：
    1. 查找"下载地址："字符串
    2. 向后查找，先遇到"..."就重新搜索
    3. 先遇到"（密码在上方youtube视频中口述）"就提取两者间的内容
    """
    print("正在按照精确方法提取paste.to链接...")
    
    start_marker = "下载地址："
    ellipsis_marker = "..."
    password_marker = "（密码在上方youtube视频中口述）"
    
    pos = 0
    while pos < len(content):
        # 查找起始标记
        start_pos = content.find(start_marker, pos)
        if start_pos == -1:
            break
        
        # 计算链接开始位置（跳过起始标记）
        link_start = start_pos + len(start_marker)
        
        # 查找两个可能的结束标记
        ellipsis_pos = content.find(ellipsis_marker, link_start)
        password_pos = content.find(password_marker, link_start)
        
        # ============= 新增调试代码开始 =============
        # 打印关键位置附近的内容片段
        debug_start = max(0, start_pos-50)  # 查看起始标记前50字符
        debug_end = min(len(content), (password_pos if password_pos != -1 else ellipsis_pos if ellipsis_pos != -1 else start_pos) + 50)
        print("\n==== 调试内容片段 ====")
        print(f"当前位置: {start_pos}")
        print(f"起始标记位置: {start_pos}-{start_pos+len(start_marker)}")
        print(f"密码标记位置: {password_pos}")
        print(f"省略号位置: {ellipsis_pos}")
        print("内容预览:")
        print(content[debug_start:debug_end])
        print("=====================\n")
        # ============= 新增调试代码结束 =============
        
        # 判断哪个标记先出现
        if password_pos != -1 and (ellipsis_pos == -1 or password_pos < ellipsis_pos):
            # 找到密码标记，提取完整链接
            link = content[link_start:password_pos].strip()
            if link.startswith("http"):
                print(f"找到完整链接: {link}")
                return link
            pos = password_pos + len(password_marker)
        elif ellipsis_pos != -1:
            # 找到省略号，跳过继续搜索
            pos = ellipsis_pos + len(ellipsis_marker)
        else:
            # 两个标记都没找到，结束搜索
            break
    
    print("未找到符合要求的paste.to链接")
    return None

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
    
    # 提取paste.to链接
    paste_link = extract_paste_link(content)
    
    if paste_link:
        print(f"\n最终提取结果: {paste_link}")
    else:
        print("\n未能提取到paste.to链接")

if __name__ == "__main__":
    main()
