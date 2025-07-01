import requests
import re
from datetime import datetime
from urllib.parse import urljoin

def find_dated_videos(channel_url):
    """
    查找指定YouTube频道中所有以日期开头的视频
    
    参数:
        channel_url (str): YouTube频道URL
        
    返回:
        list: 包含所有日期视频信息的列表，按日期排序
    """
    
    print(f"[调试] 开始处理频道: {channel_url}")
    
    try:
        # 发送HTTP请求获取频道页面
        print("[调试] 正在发送HTTP请求获取频道页面...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()
        print("[调试] 成功获取频道页面内容")
        
        # 将响应内容转换为文本
        page_content = response.text
        print(f"[调试] 页面内容长度: {len(page_content)} 字符")
        
        # 查找所有日期格式的标题和对应的视频ID
        print("[调试] 正在搜索日期格式的视频...")
        
        # 匹配中文日期格式(2025年7月1日)和后面的视频ID
        date_pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日).*?"url":"(/watch\?v=[^"]+)"')
        matches = date_pattern.finditer(page_content)
        
        videos = []
        found_count = 0
        
        for match in matches:
            found_count += 1
            date_str = match.group(1)
            video_path = match.group(2)
            video_url = urljoin('https://www.youtube.com', video_path)
            
            try:
                # 将中文日期转换为datetime对象
                date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                videos.append({
                    'date_str': date_str,
                    'date_obj': date_obj,
                    'url': video_url
                })
                print(f"[调试] 找到视频 #{found_count}: 日期={date_str}, URL={video_url}")
            except ValueError as e:
                print(f"[警告] 日期解析失败: {date_str}, 错误: {e}")
                continue
        
        if not videos:
            print("[警告] 没有找到以日期开头的视频")
            return None
        
        # 按日期排序(从新到旧)
        print("[调试] 正在按日期排序视频...")
        videos.sort(key=lambda x: x['date_obj'], reverse=True)
        
        print(f"[信息] 共找到 {len(videos)} 个日期视频")
        for i, video in enumerate(videos, 1):
            print(f"[信息] {i}. {video['date_str']} - {video['url']}")
        
        return videos
        
    except requests.RequestException as e:
        print(f"[错误] 网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"[错误] 处理过程中发生异常: {e}")
        return None

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    dated_videos = find_dated_videos(channel_url)
    
    if dated_videos:
        latest_video = dated_videos[0]
        print("\n最终结果:")
        print(f"最新视频日期: {latest_video['date_str']}")
        print(f"视频链接: {latest_video['url']}")
        
        # 这里可以添加代码来实际访问该视频
        # 例如使用webbrowser.open(latest_video['url'])
    else:
        print("未能找到符合条件的视频")
