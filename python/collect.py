import requests
import re
from datetime import datetime
from urllib.parse import urljoin, unquote
import json

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

def extract_encoded_paste_links(content):
    """精确查找编码后的paste.to链接"""
    print("正在搜索编码后的paste.to链接...")
    links = []
    
    # 查找所有编码后的paste.to链接
    matches = re.finditer(r'https%3A%2F%2Fpaste\.to[^\\\s]+', content)
    
    for match in matches:
        encoded_url = match.group()
        try:
            # URL解码
            decoded_url = unquote(encoded_url)
            links.append(decoded_url)
            print(f"找到编码链接: {encoded_url} -> 解码后: {decoded_url}")
        except Exception as e:
            print(f"解码失败: {encoded_url}, 错误: {str(e)}")
    
    return links

def get_paste_json(paste_url):
    """获取paste.to的JSON数据"""
    try:
        # 提取paste ID
        paste_id = paste_url.split('?')[-1].split('#')[0]
        
        # 构造API请求URL
        api_url = f"https://paste.to/?{paste_id}&json=1"
        
        # 添加必要的headers
        headers = {
            'X-Requested-With': 'JSONHttpRequest',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"\n正在请求API: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 解析JSON响应
        json_data = response.json()
        return json_data
        
    except Exception as e:
        print(f"获取paste.to JSON数据失败: {str(e)}")
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
    
    print("正在精确搜索编码后的paste.to链接...")
    paste_links = extract_encoded_paste_links(content)
    
    if not paste_links:
        print("\n未找到paste.to链接")
        return
    
    print("\n找到的paste.to链接:")
    for i, link in enumerate(paste_links, 1):
        print(f"{i}. {link}")
    
    # 获取第一个paste.to链接的JSON数据
    first_paste = paste_links[0]
    print(f"\n正在处理第一个链接: {first_paste}")
    
    json_data = get_paste_json(first_paste)
    if json_data:
        print("\n成功获取JSON数据:")
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        
        # 提取关键信息
        print("\n关键信息:")
        print(f"状态: {json_data.get('status')}")
        print(f"ID: {json_data.get('id')}")
        print(f"URL: {json_data.get('url')}")
        print(f"版本: {json_data.get('v')}")
        print(f"加密参数: {json_data.get('adata')}")
    else:
        print("\n未能获取JSON数据")

if __name__ == "__main__":
    main()
