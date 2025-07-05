import requests
import json
import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import HMAC, SHA256

def decrypt_privatebin_v176(paste_url, password="1010"):
    try:
        # 1. 从URL提取ID和hash
        url_parts = paste_url.split('?')
        paste_id = url_parts[-1].split('#')[0] if '?' in paste_url else None
        paste_hash = url_parts[-1].split('#')[1] if '#' in url_parts[-1] else None

        if not paste_hash:
            return "错误: URL中没有找到加密hash"

        # 2. Base64解码hash部分 (兼容URL-safe和标准Base64)
        padding = len(paste_hash) % 4
        if padding:
            paste_hash += '=' * (4 - padding)
        
        try:
            decoded = base64.urlsafe_b64decode(paste_hash)
        except:
            decoded = base64.b64decode(paste_hash)
        
        print(f"Hash解码长度: {len(decoded)}字节")

        # 3. PrivateBin 1.7.6 数据格式解析
        # 结构: [版本(1字节)] + [salt(16字节)] + [iv(16字节)] + [加密数据]
        if len(decoded) < 33:  # 1+16+16=33
            return "错误: 数据长度不足"
        
        version = decoded[0]
        salt = decoded[1:17]
        iv = decoded[17:33]
        ciphertext = decoded[33:] if len(decoded) > 33 else b''

        print(f"版本: {version}")
        print(f"Salt: {salt.hex()}")
        print(f"IV: {iv.hex()}")
        print(f"加密数据长度: {len(ciphertext)}字节")

        # 4. 密钥派生 (PBKDF2-HMAC-SHA256)
        key = PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=32,       # AES-256密钥长度
            count=100000,   # PrivateBin 1.7.6默认迭代次数
            prf=lambda p, s: HMAC.new(p, s, SHA256).digest()
        )

        # 5. AES-256-CBC解密
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)

        # 6. 移除PKCS7填充
        pad_length = decrypted[-1]
        decrypted = decrypted[:-pad_length]

        # 7. 解压缩 (zlib)
        try:
            decompressed = zlib.decompress(decrypted)
            return decompressed.decode('utf-8')
        except:
            return decrypted.decode('utf-8', errors='ignore')

    except Exception as e:
        return f"解密过程中出错: {str(e)}"

# 使用示例
if __name__ == "__main__":
    # 你的paste.to链接
    paste_url = "https://paste.to/?7720f5f08a224bc6#2RtyqaPSVNtfaQMcpYxLmBpqhjpHUAYswrEUbxcZyG4W"
    
    # 解密 (使用默认密码1010)
    result = decrypt_privatebin_v176(paste_url)
    print("\n解密结果:")
    print(result)
