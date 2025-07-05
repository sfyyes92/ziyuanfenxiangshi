import requests
import re
import base64
import zlib
import json
from urllib.parse import urljoin, unquote
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

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

def get_paste_data(paste_url):
    """获取paste.to的JSON数据"""
    try:
        paste_id = paste_url.split('?')[-1].split('#')[0]
        api_url = f"https://paste.to/?{paste_id}&json=1"
        
        headers = {
            'X-Requested-With': 'JSONHttpRequest',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"\n正在请求API: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
        
    except Exception as e:
        print(f"获取paste.to数据失败: {str(e)}")
        return None

def decrypt_paste(paste_data, password):
    """解密paste.to内容"""
    try:
        # 提取加密参数
        ciphertext = base64.b64decode(paste_data['ct'])
        adata = paste_data['adata']
        
        # 从adata中提取参数
        iv = base64.b64decode(adata[0][0])
        salt = base64.b64decode(adata[0][1])
        iterations = adata[0][2]
        key_size = adata[0][3] // 8
        tag_size = adata[0][4] // 8
        algorithm = adata[0][5]
        mode = adata[0][6]
        compression = adata[0][7]
        
        # 派生密钥
        key = PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=key_size,
            count=iterations,
            hmac_hash_module=SHA256
        )
        
        # 分离密文和认证标签（GCM模式）
        tag = ciphertext[-tag_size:]
        ciphertext = ciphertext[:-tag_size]
        
        # 解密
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        cipher.update(b'')  # 空adata
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        
        # 处理压缩
        if compression == 'zlib':
            try:
                return zlib.decompress(decrypted).decode('utf-8')
            except zlib.error:
                pass
        
        # 尝试直接解码
        try:
            return decrypted.decode('utf-8')
        except UnicodeDecodeError:
            return None
            
    except Exception as e:
        print(f"解密失败: {str(e)}")
        return None

def main():
    # 配置参数
    channel_url = "https://www.youtube.com/@ZYFXS"
    known_password = "1010"
    
    print("="*50)
    print("开始获取YouTube频道最新视频...")
    print("="*50)
    
    # 1. 获取最新视频
    latest_video = find_latest_video(channel_url)
    if not latest_video:
        print("未找到符合条件的视频")
        return
    
    print(f"\n找到最新视频: {latest_video['date_str']}")
    print(f"视频链接: {latest_video['url']}")
    
    # 2. 获取视频内容
    print("\n正在获取视频页面内容...")
    content = get_youtube_content(latest_video['url'])
    if not content:
        print("无法获取页面内容")
        return
    
    # 3. 提取paste.to链接
    print("\n正在搜索编码后的paste.to链接...")
    paste_links = extract_encoded_paste_links(content)
    
    if not paste_links:
        print("\n未找到paste.to链接")
        return
    
    # 4. 处理第一个找到的链接
    first_paste = paste_links[0]
    print(f"\n正在处理链接: {first_paste}")
    
    # 5. 获取paste数据
    paste_data = get_paste_data(first_paste)
    if not paste_data:
        print("\n未能获取paste数据")
        return
    
    print("\n获取到的paste数据:")
    print(json.dumps(paste_data, indent=2, ensure_ascii=False))
    
    # 6. 使用已知密码解密
    print(f"\n尝试使用密码 '{known_password}' 解密...")
    plaintext = decrypt_paste(paste_data, known_password)
    
    if plaintext:
        print("\n" + "="*50)
        print("解密成功！内容如下:")
        print("="*50)
        print(plaintext)
    else:
        print("\n解密失败，请检查密码或加密参数")

if __name__ == "__main__":
    # 安装必要库: pip install requests pycryptodome
    from datetime import datetime
    main()
