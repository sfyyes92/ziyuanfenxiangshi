import requests
import re
from datetime import datetime
from urllib.parse import urljoin

def get_enhanced_content(url):
    """获取完整页面内容的强化版"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    for _ in range(3):  # 最多重试3次
        try:
            print(f"[请求] 正在获取 {url}...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            content = response.text
            print(f"[成功] 获取内容长度: {len(content)/1024:.1f} KB")
            
            # 关键内容验证
            required_markers = [
                'window.ytcfg.set(',
                'var ytInitialData =',
                'videoId'
            ]
            if all(marker in content for marker in required_markers):
                return content
            else:
                print("[警告] 内容完整性校验未通过，尝试备用方案...")
                return get_fallback_content(url)
                
        except Exception as e:
            print(f"[异常] 请求失败: {str(e)}")
            continue
    
    raise Exception("无法获取完整内容")

def get_fallback_content(url):
    """备用获取方案：分段获取关键数据"""
    print("[备用方案] 启动分段获取...")
    critical_parts = []
    
    # 分段获取关键脚本内容
    script_urls = [
        urljoin(url, '/youtubei/v1/player'),
        urljoin(url, '/youtubei/v1/browse')
    ]
    
    for s_url in script_urls:
        try:
            resp = requests.get(s_url, timeout=10)
            if resp.status_code == 200:
                critical_parts.append(resp.text)
        except:
            continue
    
    return "\n".join(critical_parts)

def parse_videos(html):
    """改进的解析方法"""
    print("[解析] 正在分析页面结构...")
    
    # 方法1：尝试从JSON数据块提取
    initial_data = re.search(r'var ytInitialData\s*=\s*({.+?});', html, re.DOTALL)
    if initial_data:
        print("[解析] 发现ytInitialData块")
        # 这里可以添加JSON解析逻辑（示例简化版）
        video_items = re.finditer(
            r'"title":{"runs":\[{"text":"(\d{4}年\d{1,2}月\d{1,2}日[^"]+)".*?"videoId":"([^"]+)"',
            initial_data.group(1)
        )
        return [
            {
                'date': datetime.strptime(m.group(1)[:11], 
                'url': f"https://youtu.be/{m.group(2)}"
            }
            for m in video_items
        ]
    
    # 方法2：回退到HTML解析
    print("[解析] 回退到HTML分析")
    return re.finditer(
        r'(\d{4}年\d{1,2}月\d{1,2}日).*?href="(/watch\?v=[^"]+)"',
        html
    )

def main():
    try:
        # 获取增强版内容
        content = get_enhanced_content("https://www.youtube.com/@ZYFXS")
        
        # 解析视频
        videos = parse_videos(content)
        if not videos:
            raise Exception("未解析到视频数据")
            
        # 找出最新视频
        latest = max(videos, key=lambda x: x['date'])
        print(f"\n最新视频: {latest['date'].strftime('%Y年%m月%d日')}")
        print(f"视频链接: {latest['url']}")
        
        # 获取视频详情页
        video_content = get_enhanced_content(latest['url'])
        
        # 搜索paste.to链接
        paste_links = re.findall(r'(https?://paste\.to/[^\s"<]+)', video_content)
        if paste_links:
            print("\n找到的 paste.to 链接:")
            for i, link in enumerate(set(paste_links), 1):  # 去重
                print(f"{i}. {link}")
        else:
            print("未找到目标链接")
            
    except Exception as e:
        print(f"[主流程错误] {str(e)}")

if __name__ == "__main__":
    main()
