import requests
import re
from datetime import datetime
from urllib.parse import urljoin, unquote
import json
import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from tqdm import tqdm  # 用于显示进度条

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
    
    videos.sort(key=lambda x: x['date_obj'], reverse=True)
    return videos[0]

def extract_encoded_paste_links(content):
    """精确查找编码后的paste.to链接"""
    print("正在搜索编码后的paste.to链接...")
    links = []
    
    matches = re.finditer(r'https%3A%2F%2Fpaste\.to[^\\\s]+', content)
    
    for match in matches:
        encoded_url = match.group()
        try:
            decoded_url = unquote(encoded_url)
            links.append(decoded_url)
            print(f"找到编码链接: {encoded_url} -> 解码后: {decoded_url}")
        except Exception as e:
            print(f"解码失败: {encoded_url}, 错误: {str(e)}")
    
    return links

def parse_paste_jsonld(json_data):
    """根据JSON-LD规范解析paste数据"""
    parsed = {
        'metadata': {},
        'encryption': {},
        'content': {}
    }
    
    parsed['status'] = json_data.get('status')
    parsed['id'] = json_data.get('id')
    parsed['url'] = json_data.get('url')
    parsed['version'] = json_data.get('v')
    
    if 'adata' in json_data:
        parsed['encryption']['adata'] = json_data['adata']
        if isinstance(json_data['adata'], list) and len(json_data['adata']) > 0:
            if isinstance(json_data['adata'][0], list):
                parsed['encryption'].update({
                    'iv': json_data['adata'][0][0],
                    'salt': json_data['adata'][0][1],
                    'iterations': json_data['adata'][0][2],
                    'key_size': json_data['adata'][0][3],
                    'tag_size': json_data['adata'][0][4],
                    'algorithm': json_data['adata'][0][5],
                    'mode': json_data['adata'][0][6],
                    'compression': json_data['adata'][0][7]
                })
    
    if 'ct' in json_data:
        parsed['content']['cipher_text'] = json_data['ct']
    
    if 'meta' in json_data:
        parsed['metadata'] = json_data['meta']
    
    if 'comments' in json_data:
        parsed['comments'] = {
            'count': json_data.get('comment_count', 0),
            'offset': json_data.get('comment_offset', 0),
            'list': json_data['comments']
        }
    
    return parsed

def get_paste_jsonld(paste_url):
    """获取并解析paste.to的JSON-LD数据"""
    try:
        paste_id = paste_url.split('?')[-1].split('#')[0]
        api_url = f"https://paste.to/?{paste_id}&json=1"
        
        headers = {
            'X-Requested-With': 'JSONHttpRequest',
            'Accept': 'application/ld+json, application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"\n正在请求API: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        return parse_paste_jsonld(json_data)
        
    except Exception as e:
        print(f"获取paste.to JSON-LD数据失败: {str(e)}")
        return None

def brute_force_decrypt(paste_data):
    """暴力破解4位数字密码"""
    if not paste_data.get('content') or not paste_data.get('encryption'):
        print("缺少解密所需的数据")
        return None
    
    ciphertext = base64.b64decode(paste_data['content'].get('cipher_text', ''))
    iv = base64.b64decode(paste_data['encryption'].get('iv', ''))
    salt = base64.b64decode(paste_data['encryption'].get('salt', ''))
    iterations = paste_data['encryption'].get('iterations', 100000)
    compression = paste_data['encryption'].get('compression', 'zlib')
    
    print("\n开始暴力破解4位数字密码...")
    
    # 生成所有4位数字组合 (0000-9999)
    passwords = [f"{i:04d}" for i in range(10000)]
    
    for password in tqdm(passwords, desc="尝试密码"):
        try:
            # 派生密钥
            key = PBKDF2(
                password.encode('utf-8'),
                salt,
                dkLen=32,  # 256-bit
                count=iterations,
                hmac_hash_module=SHA256
            )
            
            # 解密
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt(ciphertext)
            
            # 处理压缩
            if compression == 'zlib':
                try:
                    plaintext = zlib.decompress(decrypted).decode('utf-8')
                    return password, plaintext
                except zlib.error:
                    pass
            
            # 尝试直接解码
            try:
                plaintext = decrypted.decode('utf-8')
                if len(plaintext) > 10:  # 简单验证解密结果是否合理
                    return password, plaintext
            except UnicodeDecodeError:
                continue
                
        except Exception:
            continue
    
    return None, None

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
    
    first_paste = paste_links[0]
    print(f"\n正在处理第一个链接: {first_paste}")
    
    paste_data = get_paste_jsonld(first_paste)
    if paste_data:
        print("\n解析后的paste数据:")
        print(json.dumps(paste_data, indent=2, ensure_ascii=False))
        
        print("\n加密参数详情:")
        print(f"IV: {paste_data['encryption'].get('iv')}")
        print(f"Salt: {paste_data['encryption'].get('salt')}")
        print(f"迭代次数: {paste_data['encryption'].get('iterations')}")
        print(f"算法: {paste_data['encryption'].get('algorithm')}-{paste_data['encryption'].get('mode')}")
        print(f"压缩: {paste_data['encryption'].get('compression')}")
        
        # 开始暴力破解
        password, plaintext = brute_force_decrypt(paste_data)
        
        if password and plaintext:
            print(f"\n破解成功! 密码: {password}")
            print("\n解密内容:")
            print(plaintext)
        else:
            print("\n未能破解密码")
    else:
        print("\n未能获取paste数据")

if __name__ == "__main__":
    # 安装必要库: pip install requests pycryptodome tqdm
    main()
