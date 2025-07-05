import json
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
import zlib

# 从JSON响应中提取加密数据
response = {
    "status": 0,
    "id": "7720f5f08a224bc6",
    # ... 其他字段 ...
    "adata": [
        ["NdetfPAOCFuiIfbuGHmC3A==", "a7vqMWO7C4Q=", 100000, 256, 128, "aes", "gcm", "zlib"],
        "plaintext",
        0,
        0
    ],
    "ct": "UGnSlI0MLwxNVszw1OSW+CHEuCSn5QMgyaIXK1iOSPwlfLssq+4C5GO+sSgM/W6dP/QRsPWf4wD28S2fL45fGvYWfBc3jJgXRKgRmqvTQ2n/SlwPDD+mBRe8TVwJ7DxJDmlR+hwHn4TfVJZS0woWXTheY9iKlB4YEGZa92X1FHIl7qKHbF3uuXJceJV08MNjWK5XaOrVkL+GQqNaFBHJdjijH5wWuhVIpB74IqMcCZZkzl8LLbz9GZJmQmWzb6yacAuSvwjtkUgnCg2TVUtm9vCocnUrTpIWYFXUJ7pWVex097pTx+mNUZTmGEsKmt391zOSK5OIB+e0XTH3NSVsoIabXFX6m7xzHs7q17A+BgDoKWus43z5l2GOzpw/GuUOvM4BgjAiFFkks3POKGGrf9OcwBLcLFCxbfybGOMNok4c9Xb1RSM+I79xKjCDGGGVGE4HBalb17Qi6jpZmTPnWoEH41JBap8KRpb7VCSWZXPC7+bxdSXTa62tguoJ1pVEhhva2eSYyzLz6t7VGjdhlY1xuBmr/ZvMJQ3bITv6ARt0XgtfH4P5cFZCu66mzo/Nx2L4Qhd0dHUSzvlBmJ+l9Ts+sBWCmVwyE+aJurcQlbCPqAS2skf/EZQiErRRtUAkAhVQnEH+sNdo6/bxnuvXOA55fRNPfw6Jw8pPIqqQ+hjWav213N6NNNv2puNAwUvJgshLIs060M8LNl9KNV+bLqPQCWbytFTRiaf9n9fC2GudClXKUp9ISZZVklOlgDgLgv6FbTS3UO2ZUkIdjsAgRKHP4bVB5oHN0VGU5N1izldv0KjKuVlbIJ9f3Y05WNR/4MvzGc9l6htWwcrqDtxv55+y++pNKpC4Cn4zcjCVMrHYAHILbKp0lzhSo7iRofrwt8lXI0l2y9EHSKDChP2/bzADDqedFo0ouroXdWRUdyOqPWdKpR8vaeH8KzDGJGBZ5YcyyriO3PmS6NY+QvLJYqOipPVe/N9Yiz6ertpfWIKEDJQu9oykL4XH4MSWnm/euhjTmU+tZtqV2D88AJXgAgUmHq7mbKMe8+IHTNcZbvwQDJm8PwbwM3xQShusu6W13vVwclzEjvNaqR7xlE8HiCWTptmsn4nvmjZWDgJ8dqGcQfnlNJrS7kJH5shPYF39dqMp26B+11IH2t8F4s/2C26BDXfTK43z5yzVMbMGQcHyyuxBVsW/+z+PMGTBNm+8nW/77f3wM+52s1365pSKUlyVE5dBgaAtMX1D7yKdMqFT/z2vptzfsD9CMBN9es61IlUVCd57J4ti6hEqWajwqGfDmJVdR7HOJrQ3eC9IkjZyRy94eLceSiPCG70="
}

# 提取加密参数
adata = response["adata"][0]
salt = b64decode(adata[0])
iv = b64decode(adata[1])
iterations = adata[2]
key_len = adata[3] // 8  # 转换为字节
tag_len = adata[4] // 8
cipher_text = b64decode(response["ct"])

# 尝试两种密码格式
passwords = [
    b"1010",  # 字符串形式
    bytes([0x01, 0x00, 0x01, 0x00])  # 字节形式
]

for password in passwords:
    try:
        # 使用scrypt派生密钥
        key = scrypt(
            password=password,
            salt=salt,
            key_len=key_len,
            N=iterations,
            r=8,
            p=1
        )
        
        # 分离密文和认证标签
        ciphertext = cipher_text[:-tag_len]
        tag = cipher_text[-tag_len:]
        
        # 创建解密器
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        
        # 解密
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        
        # 解压缩
        decompressed = zlib.decompress(decrypted)
        
        print(f"成功解密 (密码格式: {password}):")
        print(decompressed.decode('utf-8'))
        break
    except Exception as e:
        print(f"解密失败 (密码格式: {password}): {str(e)}")
