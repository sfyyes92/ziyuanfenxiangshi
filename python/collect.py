import base64
import json
import zlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

# 从你的 JSON 数据中提取加密参数
json_data = """
{
  "status": 0,
  "id": "7720f5f08a224bc6",
  "url": "/?pasteid=7720f5f08a224bc6&json=1?7720f5f08a224bc6",
  "adata": [
    [
      "NdetfPAOCFuiIfbuGHmC3A==",
      "a7vqMWO7C4Q=",
      100000,
      256,
      128,
      "aes",
      "gcm",
      "zlib"
    ],
    "plaintext",
    0,
    0
  ],
  "meta": {
    "time_to_live": 573272
  },
  "v": 2,
  "ct": "UGnSlI0MLwxNVszw1OSW+CHEuCSn5QMgyaIXK1iOSPwlfLssq+4C5GO+sSgM/W6dP/QRsPWf4wD28S2fL45fGvYWfBc3jJgXRKgRmqvTQ2n/SlwPDD+mBRe8TVwJ7DxJDmlR+hwHn4TfVJZS0woWXTheY9iKlB4YEGZa92X1FHIl7qKHbF3uuXJceJV08MNjWK5XaOrVkL+GQqNaFBHJdjijH5wWuhVIpB74IqMcCZZkzl8LLbz9GZJmQmWzb6yacAuSvwjtkUgnCg2TVUtm9vCocnUrTpIWYFXUJ7pWVex097pTx+mNUZTmGEsKmt391zOSK5OIB+e0XTH3NSVsoIabXFX6m7xzHs7q17A+BgDoKWus43z5l2GOzpw/GuUOvM4BgjAiFFkks3POKGGrf9OcwBLcLFCxbfybGOMNok4c9Xb1RSM+I79xKjCDGGGVGE4HBalb17Qi6jpZmTPnWoEH41JBap8KRpb7VCSWZXPC7+bxdSXTa62tguoJ1pVEhhva2eSYyzLz6t7VGjdhlY1xuBmr/ZvMJQ3bITv6ARt0XgtfH4P5cFZCu66mzo/Nx2L4Qhd0dHUSzvlBmJ+l9Ts+sBWCmVwyE+aJurcQlbCPqAS2skf/EZQiErRRtUAkAhVQnEH+sNdo6/bxnuvXOA55fRNPfw6Jw8pPIqqQ+hjWav213N6NNNv2puNAwUvJgshLIs060M8LNl9KNV+bLqPQCWbytFTRiaf9n9fC2GudClXKUp9ISZZVklOlgDgLgv6FbTS3UO2ZUkIdjsAgRKHP4bVB5oHN0VGU5N1izldv0KjKuVlbIJ9f3Y05WNR/4MvzGc9l6htWwcrqDtxv55+y++pNKpC4Cn4zcjCVMrHYAHILbKp0lzhSo7iRofrwt8lXI0l2y9EHSKDChP2/bzADDqedFo0ouroXdWRUdyOqPWdKpR8vaeH8KzDGJGBZ5YcyyriO3PmS6NY+QvLJYqOipPVe/N9Yiz6ertpfWIKEDJQu9oykL4XH4MSWnm/euhjTmU+tZtqV2D88AJXgAgUmHq7mbKMe8+IHTNcZbvwQDJm8PwbwM3xQShusu6W13vVwclzEjvNaqR7xlE8HiCWTptmsn4nvmjZWDgJ8dqGcQfnlNJrS7kJH5shPYF39dqMp26B+11IH2t8F4s/2C26BDXfTK43z5yzVMbMGQcHyyuxBVsW/+z+PMGTBNm+8nW/77f3wM+52s1365pSKUlyVE5dBgaAtMX1D7yKdMqFT/z2vptzfsD9CMBN9es61IlUVCd57J4ti6hEqWajwqGfDmJVdR7HOJrQ3eC9IkjZyRy94eLceSiPCG70=",
  "comments": [],
  "comment_count": 0,
  "comment_offset": 0,
  "@context": "?jsonld=paste"
}
"""

# 解析 JSON
data = json.loads(json_data)
ct = data["ct"]  # 密文
adata = data["adata"][0]  # 加密参数

# 提取加密参数
salt = base64.b64decode(adata[0])  # 盐值
iv = base64.b64decode(adata[1])  # 初始化向量
iterations = adata[2]  # PBKDF2 迭代次数
key_size = adata[3]  # 密钥长度 (256 bits)
tag_size = adata[4]  # GCM 认证标签长度 (128 bits)
cipher = adata[5]  # 加密算法 (aes)
mode = adata[6]  # 加密模式 (gcm)
compression = adata[7]  # 压缩方式 (zlib)

password = "1010"  # 已知密码

# 1. 使用 PBKDF2 从密码派生密钥
key = PBKDF2(
    password.encode("utf-8"),
    salt,
    dkLen=key_size // 8,  # 256 bits = 32 bytes
    count=iterations,
)

# 2. 解密 AES-GCM
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
try:
    # Base64 解码密文
    ciphertext = base64.b64decode(ct)
    # 解密（GCM 模式会自动处理认证标签）
    plaintext = cipher.decrypt(ciphertext)
except Exception as e:
    print("解密失败:", e)
    exit(1)

# 3. 解压缩（如果是 zlib 压缩）
if compression == "zlib":
    try:
        plaintext = zlib.decompress(plaintext)
    except:
        print("解压缩失败，可能是数据未压缩")
        pass  # 可能数据未压缩

# 4. 输出明文
print("解密后的明文:")
print(plaintext.decode("utf-8"))
