import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urljoin

def get_latest_date_video(channel_url):
    """
    获取指定YouTube频道中最新日期的视频
    
    参数:
        channel_url (str): YouTube频道URL
        
    返回:
        dict: 包含最新日期视频信息的字典，包括标题、URL和日期
    """
    
    print(f"[调试] 开始处理频道: {channel_url}")
    
    try:
        # 发送HTTP请求获取频道页面
        print("[调试] 正在发送HTTP请求获取频道页面...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(channel_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        print("[调试] 成功获取频道页面内容")
        
        # 解析HTML内容
        print("[调试] 正在解析HTML内容...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有视频链接 - 这里的选择器可能需要根据YouTube的实际HTML结构调整
        # YouTube的HTML结构经常变化，这里是一个示例选择器
        video_elements = soup.select('a#video-title-link')  # 可能需要调整
        
        print(f"[调试] 找到 {len(video_elements)} 个视频元素")
        
        date_pattern = re.compile(r'^(\d{4}年\d{1,2}月\d{1,2}日)')
        dated_videos = []
        
        # 遍历视频元素，查找以日期开头的标题
        print("[调试] 正在筛选以日期开头的视频...")
        for idx, element in enumerate(video_elements, 1):
            title = element.get('title', '').strip()
            print(f"[调试] 检查视频 #{idx}: 标题='{title}'")
            
            match = date_pattern.match(title)
            if match:
                date_str = match.group(1)
                video_url = urljoin('https://www.youtube.com', element.get('href', ''))
                
                try:
                    # 将中文日期转换为datetime对象以便比较
                    date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                    dated_videos.append({
                        'title': title,
                        'url': video_url,
                        'date': date_obj,
                        'date_str': date_str
                    })
                    print(f"[调试] 找到日期视频: {date_str} - {title}")
                except ValueError as e:
                    print(f"[警告] 日期解析失败: {date_str}, 错误: {e}")
                    continue
        
        if not dated_videos:
            print("[警告] 没有找到以日期开头的视频")
            return None
        
        # 按日期排序，获取最新视频
        print("[调试] 正在按日期排序视频...")
        dated_videos.sort(key=lambda x: x['date'], reverse=True)
        latest_video = dated_videos[0]
        
        print(f"[信息] 找到的最新日期视频: {latest_video['date_str']} - {latest_video['title']}")
        print(f"[信息] 视频URL: {latest_video['url']}")
        
        return latest_video
        
    except requests.RequestException as e:
        print(f"[错误] 网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"[错误] 处理过程中发生异常: {e}")
        return None

if __name__ == "__main__":
    channel_url = "https://www.youtube.com/@ZYFXS"
    latest_video = get_latest_date_video(channel_url)
    
    if latest_video:
        print("\n最终结果:")
        print(f"最新视频标题: {latest_video['title']}")
        print(f"发布日期: {latest_video['date_str']}")
        print(f"视频链接: {latest_video['url']}")
        
        # 这里可以添加代码来实际访问该视频
        # 例如使用webbrowser.open(latest_video['url'])
    else:
        print("未能找到符合条件的视频")
