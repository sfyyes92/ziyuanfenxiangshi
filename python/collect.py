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
        content_length = len(page_content)
        print(f"[调试] 页面内容长度: {content_length} 字符")
        
        # 输出完整内容到文件
        with open('youtube_channel_content.txt', 'w', encoding='utf-8') as f:
            f.write(page_content)
        print("[信息] 已将完整页面内容保存到 youtube_channel_content.txt")
        
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

def search_paste_links_in_file(filename):
    """
    在文件中搜索paste.to链接并打印每个链接及其后100个字符
    
    参数:
        filename (str): 要搜索的文件名
        
    返回:
        int: 找到的链接数量
    """
    try:
        print(f"\n[信息] 正在在文件 {filename} 中搜索paste.to链接...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配所有paste.to链接
        paste_pattern = re.compile(r'(https?://paste\.to/[^\s"<]+)')
        matches = paste_pattern.finditer(content)
        
        found_count = 0
        
        for match in matches:
            found_count += 1
            paste_link = match.group(1)
            start_pos = match.start()
            end_pos = min(start_pos + len(paste_link) + 100, len(content))
            context = content[start_pos:end_pos]
            
            print(f"\n[找到链接 #{found_count}]")
            print(f"完整链接: {paste_link}")
            print("链接及其后100字符内容:")
            print("-" * 50)
            print(context)
            print("-" * 50)
        
        if found_count == 0:
            print("[警告] 未找到任何paste.to链接")
        else:
            print(f"\n[信息] 共找到 {found_count} 个paste.to链接")
        
        return found_count
        
    except FileNotFoundError:
        print(f"[错误] 文件未找到: {filename}")
        return 0
    except Exception as e:
        print(f"[错误] 搜索链接失败: {e}")
        return 0

if __name__ == "__main__":
    # 查找最新日期的视频
    channel_url = "https://www.youtube.com/@ZYFXS"
    dated_videos = find_dated_videos(channel_url)
    
    if dated_videos:
        latest_video = dated_videos[0]
        print("\n[信息] 最新视频信息:")
        print(f"发布日期: {latest_video['date_str']}")
        print(f"视频链接: {latest_video['url']}")
        
        # 获取并保存视频页面内容
        print("\n[信息] 正在获取最新视频页面内容...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(latest_video['url'], headers=headers)
            response.raise_for_status()
            
            with open('youtube_video_content.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("[信息] 已将视频页面内容保存到 youtube_video_content.txt")
            print(f"[信息] 内容长度: {len(response.text)} 字符")
            
            # 在文件中搜索paste.to链接
            search_paste_links_in_file('youtube_video_content.txt')
            
        except Exception as e:
            print(f"[错误] 获取视频页面内容失败: {e}")
    else:
        print("未能找到符合条件的视频")
