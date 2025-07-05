import re
import requests
import json
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import HMAC, SHA256
import base64
import zlib
from urllib.parse import urljoin, unquote
from datetime import datetime

# 你的原始函数保持不变
def get_youtube_content(url):
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

# 新增的解密函数
def decrypt_paste(paste_url, password="1010"):
    """解密paste.to内容"""
    try:
        # 1. 从URL提取paste ID和hash
        paste_id = paste_url.split('?')[-1].split('#')[0]
        paste_hash = paste_url.split('#')[-1] if '#' in paste_url else None
        
        if not paste_hash:
            print("错误: URL中没有找到加密hash")
            return None

        # 2. 尝试API方式获取数据
        api_url = f"https://paste.to/?{paste_id}"
        headers = {"X-Requested-With": "JSONHttpRequest"}
        
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                print("API返回数据:", json.dumps(data, indent=2))
                
                # 3. 解析加密参数
                ct = data["ct"]  # 加密数据
                adata = data["adata"]  # 加密元数据
                
                # 4. 解密流程
                iterations = 100000  # 默认迭代次数
                salt = b'salt_example'  # 需要根据实际adata结构调整
                iv = b'iv_example_16byte'  # 需要根据实际adata结构调整
                
                key = PBKDF2(password.encode(), salt, dkLen=32, count=iterations,
                            prf=lambda p,s: HMAC.new(p,s,SHA256).digest())
                
                cipher = AES.new(key, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(base64.b64decode(ct))
                
                try:
                    plaintext = zlib.decompress(decrypted).decode("utf-8")
                    return plaintext
                except:
                    return decrypted.decode("utf-8", errors="ignore")
        
        except requests.exceptions.RequestException:
            print("API请求失败，尝试直接解密hash...")
        
        # 3. 直接解密hash（如果API不可用）
        decoded = base64.urlsafe_b64decode(paste_hash + "==")
        print(f"Hash解码长度: {len(decoded)}字节")
        
        if len(decoded) >= 32:
            salt = decoded[:16]
            iv = decoded[16:32]
            ciphertext = decoded[32:] if len(decoded) > 32 else b''
            
            key = PBKDF2(password.encode(), salt, dkLen=32, count=100000,
                        prf=lambda p,s: HMAC.new(p,s,SHA256).digest())
            
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            
            try:
                return zlib.decompress(decrypted).decode("utf-8")
            except:
                return decrypted.decode("utf-8", errors="ignore")
        
        return "无法解密：数据长度不足"
    
    except Exception as e:
        return f"解密过程中出错: {str(e)}"

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
    
    # 尝试解密第一个链接
    first_paste = paste_links[0]
    print(f"\n正在尝试解密第一个链接: {first_paste}")
    
    # 使用默认密码1010尝试解密
    decrypted_content = decrypt_paste(first_paste)
    
    print("\n解密结果:")
    print(decrypted_content if decrypted_content else "解密失败")

if __name__ == "__main__":
    main()
