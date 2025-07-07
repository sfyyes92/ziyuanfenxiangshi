import base64
import zlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

# 输入参数
password = "3030".encode("utf-8")  # 已知密码
salt = base64.b64decode("ZfhhNfzsgqM=")  # Salt
iv = base64.b64decode("qfeJfPb/rkw5wvfc1dSxNA==")  # IV
ciphertext = base64.b64decode("X0DpQ387vg5w131MF6htU4VpV0Y+u3IAY4wA7m7mbh3tCgunTfV/UmH0vAastQMcYIu/4+CB4+i+MldCoDqZ3tSjImzz1YarYWwbuoNQM9ZEBEck1vmMImYZDJztN/SeXVJ+iA+aWcS6gdQJXijxeGKCglrS+gLzXxY0FaI8kmtmAQBgBgl2QExOACFJSaon3Dtahe/8OrSKQjSBHUV61+YBhHmtVkZgGXNGV4+k709A3TqPWdNf5nJaPgzMpecw8LR1VnJH1wU3WMOSrS2qBhhgNidEZMhNKkvwNmU/AGo2HzsU7ETrYG13ZSIRkWJA7jxcwUT3OaXX+0AgLFO8v6ohB5Kpmg31JF9HHn0mdhtkiZINTea5eb2rpygMpXt4pDSiXEs6qvQiputHB86VlifQs17DugBJ6XJ0qjL4F+E9SGSJKe/iKTgkpDLCX9asf1FPc5CshtlBHtnxP7lfeahc5RNvwQGPRtXSMA22BsFunCbHcUn+enJr3z/suihzKpaysfOTU531znOfECIs4IK8kjATyTCKdOCvCWkJq2Tvd217g+xBRipeeXcsY9tVrcyOrH3NzbtqosIlvMg27mRkJ0Om22Nkm/Uq5Uno82MpP9ksWRCP4qN6UJG7yROTJkdRsfRR9/vA6iUgOUuGwdMhV5WQfi/t8lBBr6U47q6I426abU2g1QgrektAdA6srhXj3ueF3vRXy1FOgzHmKN7qo6it2JGz9MzMgMA5iZ1llsXLVLGCVRMcbugEJCYYESQ+l1/0bhorRfISVoqIDXMbUdPff/6myE2Xq9pTZ+X9aikiAa1SGZ1DRM8nyG6VKL7sNTT6GE8upxu56p5TGmUCSCf+3HmJ6LPpSiMmBA7dFUj6H8ZHIFVE42FIx5+WBrbu+aRQhmfcAPxo10sz675JqVxGTtDyY1Fxh6XwcOPsoeY8Nnv8Cs6YhgNEUaTZqBH5GhXxeoCWJyHaRToD5JP73WraaToWF+uA8AF6/QuS1XwuMimkJosBpTWsa9I8ZtOH4yA1t2yWnu3HgngiRzA2kUov2jdN2N74CmIeKdfrIhxcz47rG9rAWRn5WgrXuXSrHctYCgMyYGL0FTBYL+M9rtHFnovvucgoUqj936UbCuDYfrPwJ/BbsnG3EnmAbqsmMvR/q+ecpa1cPqBEs7ZW4UOxBecThga6Ye+s1IhbzMZLdkPPaFcCgN6IUMZe9VmKScB0fEh+qhUJdv4yTL7bqoSeESs0rw9RttU6McQGD1eiII82igf...")  # 密文
iterations = 100000  # PBKDF2 迭代次数

# 1. 使用 PBKDF2 从密码和 Salt 派生密钥
key = PBKDF2(password, salt, dkLen=32, count=iterations)  # AES-256 需要 32 字节密钥

# 2. 解密 AES-GCM（GCM 模式需要处理认证标签）
# 假设密文最后 16 字节是 GCM 的 tag
tag = ciphertext[-16:]  # GCM 认证标签
ciphertext = ciphertext[:-16]  # 实际密文

cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
plaintext = cipher.decrypt_and_verify(ciphertext, tag)  # 解密并验证完整性

# 3. 解压 zlib（如果压缩过）
try:
    plaintext = zlib.decompress(plaintext)
except:
    pass  # 如果没有压缩，直接跳过

# 4. 输出明文
print("解密结果:", plaintext.decode("utf-8"))
