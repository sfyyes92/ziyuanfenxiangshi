import base64
import hashlib
import zlib
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad

# 提供的数据
password = "3030"
iv = base64.b64decode("qfeJfPb/rkw5wvfc1dSxNA==")
salt = base64.b64decode("ZfhhNfzsgqM=")
iterations = 100000
key_size = 256 // 8  # in bytes
tag_size = 128 // 8  # in bytes
cipher_text_b64 = """
X0DpQ387vg5w131MF6htU4VpV0Y+u3IAY4wA7m7mbh3tCgunTfV/UmH0vAastQMcYIu/4+CB4+i+MldCoDqZ3tSjImzz1YarYWwbuoNQM9ZEBEck1vmMImYZDJztN/SeXVJ+iA+aWcS6gdQJXijxeGKCglrS+gLzXxY0FaI8kmtmAQBgBgl2QExOACFJSaon3Dtahe/8OrSKQjSBHUV61+YBhHmtVkZgGXNGV4+k709A3TqPWdNf5nJaPgzMpecw8LR1VnJH1wU3WMOSrS2qBhhgNidEZMhNKkvwNmU/AGo2HzsU7ETrYG13ZSIRkWJA7jxcwUT3OaXX+0AgLFO8v6ohB5Kpmg31JF9HHn0mdhtkiZINTea5eb2rpygMpXt4pDSiXEs6qvQiputHB86VlifQs17DugBJ6XJ0qjL4F+E9SGSJKe/iKTgkpDLCX9asf1FPc5CshtlBHtnxP7lfeahc5RNvwQGPRtXSMA22BsFunCbHcUn+enJr3z/suihzKpaysfOTU531znOfECIs4IK8kjATyTCKdOCvCWkJq2Tvd217g+xBRipeeXcsY9tVrcyOrH3NzbtqosIlvMg27mRkJ0Om22Nkm/Uq5Uno82MpP9ksWRCP4qN6UJG7yROTJkdRsfRR9/vA6iUgOUuGwdMhV5WQfi/t8lBBr6U47q6I426abU2g1QgrektAdA6srhXj3ueF3vRXy1FOgzHmKN7qo6it2JGz9MzMgMA5iZ1llsXLVLGCVRMcbugEJCYYESQ+l1/0bhorRfISVoqIDXMbUdPff/6myE2Xq9pTZ+X9aikiAa1SGZ1DRM8nyG6VKL7sNTT6GE8upxu56p5TGmUCSCf+3HmJ6LPpSiMmBA7dFUj6H8ZHIFVE42FIx5+WBrbu+aRQhmfcAPxo10sz675JqVxGTtDyY1Fxh6XwcOPsoeY8Nnv8Cs6YhgNEUaTZqBH5GhXxeoCWJyHaRToD5JP73WraaToWF+uA8AF6/QuS1XwuMimkJosBpTWsa9I8ZtOH4yA1t2yWnu3HgngiRzA2kUov2jdN2N74CmIeKdfrIhxcz47rG9rAWRn5WgrXuXSrHctYCgMyYGL0FTBYL+M9rtHFnovvucgoUqj936UbCuDYfrPwJ/BbsnG3EnmAbqsmMvR/q+ecpa1cPqBEs7ZW4UOxBecThga6Ye+s1IhbzMZLdkPPaFcCgN6IUMZe9VmKScB0fEh+qhUJdv4yTL7bqoSeESs0rw9RttU6McQGD1eiII82igXcMYF52QR9SHJCBOZ7US8WkrLeID7DKIVPzIPuBFBHrbYU1n7r9y2ctTMrsEN7OVLWoCOKA9132w==
"""

# 清理空白字符
cipher_text = base64.b64decode(cipher_text_b64.strip())

# Step 1: Derive key using PBKDF2
key = PBKDF2(password, salt, dkLen=key_size, count=iterations, hmac_hash_module=hashlib.sha256)

# Step 2: Split cipher text into encrypted_data and tag
encrypted_data = cipher_text[:-tag_size]
tag = cipher_text[-tag_size:]

# Step 3: AES-GCM decryption
cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
try:
    cipher.update(b"plaintext")  # adata == mode name (from encryption)
    decrypted_packed = cipher.decrypt_and_verify(encrypted_data, tag)
except ValueError as e:
    print("Decryption failed:", e)
    exit()

# Step 4: Decompress with zlib
try:
    plain_text = zlib.decompress(decrypted_packed).decode('utf-8')
    print("✅ Decrypted content:")
    print(plain_text)
except Exception as e:
    print("Zlib decompression failed:", e)
